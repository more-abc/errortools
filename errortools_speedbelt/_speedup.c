#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* C speedup module for errortools.
 *
 * Provides optimized implementations of exception-handling hot paths used by
 * ``_errortools.future``:
 *
 *   - fast_issubclass_check: Quick exception type hierarchy checking
 *   - fast_append_exception : Efficient exception list append operation
 *   - fast_suppress_exit    : Combined None-check + issubclass for __exit__
 *
 * The functions are tuned for the common case where the exception type raised
 * is *exactly* one of the suppressed types.  In that case we can avoid the
 * relatively expensive ``PyObject_IsSubclass`` call (which walks the MRO and
 * may invoke ``__subclasscheck__``) and answer with a simple pointer
 * comparison.
 */

/* --- Python version compatibility ---------------------------------------- */

/* ``Py_IsNone`` and ``Py_NewRef`` were added in Python 3.10; the GIL slot and
 * multi-interpreter slots were added in 3.12/3.13.  We feature-gate the use
 * of those so the module still builds on the minimum supported version
 * (Python 3.8). */
#if PY_VERSION_HEX >= 0x030A0000
#define SPEEDUP_IS_NONE(x) Py_IsNone(x)
#define SPEEDUP_NEW_REF(x) Py_NewRef(x)
#else
#define SPEEDUP_IS_NONE(x) ((x) == Py_None)
#define SPEEDUP_NEW_REF(x) \
    do {                   \
        Py_INCREF(x);      \
    } while (0)
#endif

/* --- Internal helpers --------------------------------------------------- */

/* Identity-based fast path for ``typ in excs``.
 *
 * Returns 1 if ``typ`` is exactly equal to one of the types in ``excs``,
 * 0 if it is not, and -1 if the fast path could not answer the question
 * (i.e. ``excs`` is neither a type nor a tuple of types).
 *
 * This avoids the relatively expensive ``PyObject_IsSubclass`` call in the
 * overwhelmingly common case where the exception raised is exactly the type
 * the caller asked about.  Note that this is *not* a full subclass check:
 * if the caller needs to also accept subclasses, the result of this
 * function is only meaningful as a fast-path early-out. */
static inline int identity_match(PyObject *typ, PyObject *excs) {
    if (PyType_Check(excs)) {
        return (typ == excs) ? 1 : 0;
    }
    if (PyTuple_Check(excs)) {
        Py_ssize_t n = PyTuple_GET_SIZE(excs);
        for (Py_ssize_t i = 0; i < n; i++) {
            if (PyTuple_GET_ITEM(excs, i) == typ) {
                return 1;
            }
        }
        return 0;
    }
    /* Unknown shape: defer to PyObject_IsSubclass. */
    return -1;
}

/* Translate the tri-state return of ``PyObject_IsSubclass`` into a fresh
 * ``bool`` reference (or ``NULL`` on error). */
static inline PyObject *bool_from_issubclass(int result) {
    if (result == -1) {
        return NULL;
    }
    return result ? Py_True : Py_False;
}

/* Combined fast-path answer for the two subclass-checking entry points.
 * Returns:
 *    1 if the identity fast path can answer ``True`` definitively,
 *    0 if it can answer ``False`` definitively (i.e. ``excs`` is an
 *      empty tuple, which by definition matches nothing),
 *   -1 if the fast path is inconclusive and the caller must fall through
 *      to the full ``PyObject_IsSubclass`` check. */
static inline int fast_path_result(PyObject *typ, PyObject *excs) {
    int fast = identity_match(typ, excs);
    if (fast == 1) {
        return 1;
    }
    if (PyTuple_Check(excs) && PyTuple_GET_SIZE(excs) == 0) {
        return 0;
    }
    return -1;
}

/* --- Public functions --------------------------------------------------- */

/* fast_issubclass_check(typ, excs) -> bool
 *
 * Check whether ``typ`` is a subclass of ``excs``.  Returns ``False`` if
 * ``typ`` is ``None``.  ``excs`` must be a class or a tuple of classes;
 * a ``TypeError`` is raised otherwise. */
static PyObject *fast_issubclass_check(PyObject *self, PyObject *const *args, Py_ssize_t nargs) {
    (void)self; /* module method - self is unused */
    if (nargs != 2) {
        PyErr_Format(PyExc_TypeError,
                     "fast_issubclass_check() takes exactly 2 arguments (%zd given)",
                     nargs);
        return NULL;
    }

    PyObject *typ = args[0];
    PyObject *excs = args[1];

    /* None never matches. */
    if (SPEEDUP_IS_NONE(typ)) {
        Py_RETURN_FALSE;
    }

    /* ``excs`` must be a class or tuple of classes. */
    if (!PyType_Check(excs) && !PyTuple_Check(excs)) {
        PyErr_SetString(PyExc_TypeError,
                        "second argument must be a class or tuple of classes");
        return NULL;
    }

    /* Fast path: identity match avoids the MRO walk entirely. */
    int fast = fast_path_result(typ, excs);
    if (fast == 1) {
        Py_RETURN_TRUE;
    }
    if (fast == 0) {
        Py_RETURN_FALSE;
    }

    /* Slow path: defer to CPython's full implementation. */
    return bool_from_issubclass(PyObject_IsSubclass(typ, excs));
}

/* fast_append_exception(list, exc) -> None
 *
 * Append ``exc`` to ``list``.  ``list`` must be a Python ``list``; a
 * ``TypeError`` is raised otherwise.  The explicit type check provides a
 * friendlier error than the ``SystemError`` raised by ``PyList_Append`` for
 * the same condition. */
static PyObject *fast_append_exception(PyObject *self, PyObject *const *args, Py_ssize_t nargs) {
    (void)self; /* module method - self is unused */
    if (nargs != 2) {
        PyErr_Format(PyExc_TypeError,
                     "fast_append_exception() takes exactly 2 arguments (%zd given)",
                     nargs);
        return NULL;
    }

    PyObject *list = args[0];
    PyObject *exc = args[1];

    if (!PyList_Check(list)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a list");
        return NULL;
    }

    if (PyList_Append(list, exc) == -1) {
        return NULL; /* exception already set by PyList_Append */
    }

    Py_RETURN_NONE;
}

/* fast_suppress_exit(typ, excs) -> bool
 *
 * Return ``True`` if ``typ`` is not ``None`` and is a subclass of one of
 * the types in ``excs``.  Designed for the ``__exit__`` slot of context
 * managers: it must never raise on the ``None`` case and should be as cheap
 * as possible on the hot "no exception" path. */
static PyObject *fast_suppress_exit(PyObject *self, PyObject *const *args, Py_ssize_t nargs) {
    (void)self; /* module method - self is unused */
    if (nargs != 2) {
        PyErr_Format(PyExc_TypeError,
                     "fast_suppress_exit() takes exactly 2 arguments (%zd given)",
                     nargs);
        return NULL;
    }

    PyObject *typ = args[0];
    PyObject *excs = args[1];

    /* Hot path: no exception pending. */
    if (SPEEDUP_IS_NONE(typ)) {
        Py_RETURN_FALSE;
    }

    /* Fast path: typ is exactly one of the suppressed types. */
    int fast = fast_path_result(typ, excs);
    if (fast == 1) {
        Py_RETURN_TRUE;
    }
    if (fast == 0) {
        Py_RETURN_FALSE;
    }

    /* Slow path: full subclass check.  This is reached for:
     *   (a) identity miss on a single class,
     *   (b) identity miss on a non-empty tuple, and
     *   (c) ``excs`` of an unexpected shape. */
    return bool_from_issubclass(PyObject_IsSubclass(typ, excs));
}

/* --- Module definition -------------------------------------------------- */

static PyMethodDef SpeedupMethods[] = {
    {
        "fast_issubclass_check",
        (PyCFunction)(void (*)(void))fast_issubclass_check,
        METH_FASTCALL,
        "fast_issubclass_check(typ, excs) -> bool\n\n"
        "Check whether *typ* is a subclass of *excs*.\n"
        "Returns ``False`` if *typ* is ``None``; *excs* must be a class or\n"
        "a tuple of classes.  Uses an identity fast path before falling back\n"
        "to :c:func:`PyObject_IsSubclass`.",
    },
    {
        "fast_append_exception",
        (PyCFunction)(void (*)(void))fast_append_exception,
        METH_FASTCALL,
        "fast_append_exception(list, exc) -> None\n\n"
        "Append *exc* to *list* (which must be a :class:`list`).",
    },
    {
        "fast_suppress_exit",
        (PyCFunction)(void (*)(void))fast_suppress_exit,
        METH_FASTCALL,
        "fast_suppress_exit(typ, excs) -> bool\n\n"
        "Return ``True`` if *typ* is not ``None`` and is a subclass of any\n"
        "type in *excs*.  Tuned for ``__exit__`` context-manager methods.",
    },
    {NULL, NULL, 0, NULL} /* Sentinel */
};

/* Multi-interpreter / free-threading slots, gated by Python version.
 *
 * On Python 3.13+ we opt out of the GIL with ``Py_MOD_GIL_NOT_USED``.  This
 * is safe because the module owns no global mutable state.  The slot
 * mechanism requires multi-phase initialization (see ``PyInit__speedup``). */
#if PY_VERSION_HEX >= 0x030D0000
static PyModuleDef_Slot speedup_slots[] = {
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL},
};
#endif

static struct PyModuleDef speedupmodule = {
    PyModuleDef_HEAD_INIT,
    "_speedup",                 /* m_name */
    "C speedup module for errortools\n\n"
    "Provides optimized implementations of exception handling operations:\n"
    "  - fast_issubclass_check: Quick exception type hierarchy checking\n"
    "  - fast_append_exception: Efficient exception list append operations\n"
    "  - fast_suppress_exit: Combined None-check + issubclass for __exit__",
    0,                          /* m_size (0 = not per-interpreter) */
    SpeedupMethods,             /* m_methods */
#if PY_VERSION_HEX >= 0x030D0000
    speedup_slots,              /* m_slots */
#else
    NULL,                       /* m_slots */
#endif
    NULL,                       /* m_traverse */
    NULL,                       /* m_clear */
    NULL,                       /* m_free */
};

PyMODINIT_FUNC PyInit__speedup(void) {
    /* ``PyModuleDef_Init`` must be used (instead of ``PyModule_Create``) when
     * the module carries ``m_slots`` -- which we do on Python 3.13+ to opt
     * out of the GIL.  On older versions the two functions are functionally
     * equivalent, so we use ``PyModuleDef_Init`` unconditionally to keep
     * the init path single-source. */
    return PyModuleDef_Init(&speedupmodule);
}
