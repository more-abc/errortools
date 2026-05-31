#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* Fast exception type checking
 *
 * Optimized check for exception type hierarchy using PyObject_IsSubclass.
 * Returns False immediately if typ is None, otherwise checks if typ is a
 * subclass of excs.
 *
 * Args:
 *   typ: The type object to check (or None)
 *   excs: The exception class(es) to check against
 *
 * Returns:
 *   True if typ is a subclass of excs, False otherwise
 *   NULL on error with exception set
 */
static PyObject* fast_issubclass_check(PyObject* self, PyObject* const* args, Py_ssize_t nargs) {
    if (nargs != 2) {
        PyErr_Format(PyExc_TypeError,
                     "fast_issubclass_check() takes exactly 2 arguments (%zd given)",
                     nargs);
        return NULL;
    }

    PyObject *typ = args[0];
    PyObject *excs = args[1];

    /* Handle None case explicitly */
    if (typ == Py_None) {
        Py_RETURN_FALSE;
    }

    /* Validate that excs is a class or tuple of classes */
    if (!PyType_Check(excs) && !PyTuple_Check(excs)) {
        PyErr_SetString(PyExc_TypeError,
                        "second argument must be a class or tuple of classes");
        return NULL;
    }

    int result = PyObject_IsSubclass(typ, excs);
    if (result == -1) {
        return NULL;  /* Exception already set by PyObject_IsSubclass */
    }

    /* Return bool directly instead of going through PyBool_FromLong */
    if (result == 1) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

/* Fast exception collector append
 *
 * Optimized append operation for adding exceptions to a list.
 *
 * Args:
 *   list: The list object to append to
 *   exc: The exception object to append
 *
 * Returns:
 *   None on success
 *   NULL on error with exception set
 */
static PyObject* fast_append_exception(PyObject* self, PyObject* const* args, Py_ssize_t nargs) {
    if (nargs != 2) {
        PyErr_Format(PyExc_TypeError,
                     "fast_append_exception() takes exactly 2 arguments (%zd given)",
                     nargs);
        return NULL;
    }

    PyObject *list = args[0];
    PyObject *exc = args[1];

    /* Validate that first argument is actually a list */
    if (!PyList_Check(list)) {
        PyErr_SetString(PyExc_TypeError, "first argument must be a list");
        return NULL;
    }

    if (PyList_Append(list, exc) == -1) {
        return NULL;  /* Exception already set by PyList_Append */
    }

    Py_RETURN_NONE;
}

/* Fast suppress exit for context managers
 *
 * Combined None-check + issubclass optimized for __exit__ methods.
 * Returns True (suppress) if typ is not None and is a subclass of excs,
 * False otherwise. Never raises on None — just returns False.
 *
 * Args:
 *   typ: The exception type (or None if no exception)
 *   excs: The exception class(es) to match against (tuple)
 *
 * Returns:
 *   True if exception should be suppressed, False otherwise
 *   NULL on error with exception set
 */
static PyObject* fast_suppress_exit(PyObject* self, PyObject* const* args, Py_ssize_t nargs) {
    if (nargs != 2) {
        PyErr_Format(PyExc_TypeError,
                     "fast_suppress_exit() takes exactly 2 arguments (%zd given)",
                     nargs);
        return NULL;
    }

    PyObject *typ = args[0];

    if (typ == Py_None) {
        Py_RETURN_FALSE;
    }

    int result = PyObject_IsSubclass(typ, args[1]);
    if (result == -1) {
        return NULL;
    }

    if (result) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}

/* Method definitions */
static PyMethodDef SpeedupMethods[] = {
    {
        "fast_issubclass_check",
        (PyCFunction)fast_issubclass_check,
        METH_FASTCALL,
        "fast_issubclass_check(typ, excs) -> bool\n\n"
        "Check if typ is a subclass of excs exception type(s).\n"
        "Returns False if typ is None, otherwise uses PyObject_IsSubclass.\n"
        "Optimized for exception handling performance."
    },
    {
        "fast_append_exception",
        (PyCFunction)fast_append_exception,
        METH_FASTCALL,
        "fast_append_exception(list, exc) -> None\n\n"
        "Append an exception to a list with minimal overhead.\n"
        "Validates that the first argument is a list."
    },
    {
        "fast_suppress_exit",
        (PyCFunction)fast_suppress_exit,
        METH_FASTCALL,
        "fast_suppress_exit(typ, excs) -> bool\n\n"
        "Return True if typ is not None and is a subclass of excs.\n"
        "Optimized for context manager __exit__ methods."
    },
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

/* Module definition */
static struct PyModuleDef speedupmodule = {
    PyModuleDef_HEAD_INIT,
    "_speedup",                 /* name */
    "C speedup module for errortools\n\n"
    "Provides optimized implementations of exception handling operations:\n"
    "  - fast_issubclass_check: Quick exception type hierarchy checking\n"
    "  - fast_append_exception: Efficient exception list append operations\n"
    "  - fast_suppress_exit: Combined None-check + issubclass for __exit__",
    -1,                         /* size */
    SpeedupMethods               /* methods */
};

/* Module initialization */
PyMODINIT_FUNC PyInit__speedup(void) {
    return PyModule_Create(&speedupmodule);
}
