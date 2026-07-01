#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

/* C speedup for errortools ignore wrapper.
 *
 * Provides:
 *   - IgnoredInfo: C-backed data holder for suppressed exception info
 *   - check_and_record: fast __exit__ implementation (type check + record)
 */

#if PY_VERSION_HEX >= 0x030A0000
#define IGNORE_IS_NONE(x) Py_IsNone(x)
#else
#define IGNORE_IS_NONE(x) ((x) == Py_None)
#endif

/* --- IgnoredInfo type ----------------------------------------------------- */

typedef struct {
    PyObject_HEAD
    PyObject *name;
    char be_ignore;
    Py_ssize_t count;
    PyObject *traceback;
    PyObject *exception;
} IgnoredInfoObject;

static void
IgnoredInfo_dealloc(IgnoredInfoObject *self)
{
    Py_XDECREF(self->name);
    Py_XDECREF(self->traceback);
    Py_XDECREF(self->exception);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject *
IgnoredInfo_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    IgnoredInfoObject *self = (IgnoredInfoObject*)type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }
    self->name = Py_None;
    Py_INCREF(Py_None);
    self->be_ignore = 0;
    self->count = 0;
    self->traceback = Py_None;
    Py_INCREF(Py_None);
    self->exception = Py_None;
    Py_INCREF(Py_None);
    return (PyObject*)self;
}

static int
IgnoredInfo_init(IgnoredInfoObject *self, PyObject *args, PyObject *kwds)
{
    (void)self;
    (void)args;
    (void)kwds;
    return 0;
}

static PyObject *
IgnoredInfo_reset(IgnoredInfoObject *self, PyObject *Py_UNUSED(ignored))
{
    Py_CLEAR(self->name);
    self->name = Py_None;
    Py_INCREF(Py_None);
    self->be_ignore = 0;
    self->count = 0;
    Py_CLEAR(self->traceback);
    self->traceback = Py_None;
    Py_INCREF(Py_None);
    Py_CLEAR(self->exception);
    self->exception = Py_None;
    Py_INCREF(Py_None);
    Py_RETURN_NONE;
}

static PyMethodDef IgnoredInfo_methods[] = {
    {"reset", (PyCFunction)IgnoredInfo_reset, METH_NOARGS,
     "reset() -> None\n\nReset all ignored error tracking state to default values."},
    {NULL, NULL, 0, NULL}
};

static PyMemberDef IgnoredInfo_members[] = {
    {"name", T_OBJECT_EX, offsetof(IgnoredInfoObject, name), 0, "exception name"},
    {"be_ignore", T_BOOL, offsetof(IgnoredInfoObject, be_ignore), 0, "whether ignored"},
    {"count", T_PYSSIZET, offsetof(IgnoredInfoObject, count), 0, "ignore count"},
    {"traceback", T_OBJECT_EX, offsetof(IgnoredInfoObject, traceback), 0, "traceback string"},
    {"exception", T_OBJECT_EX, offsetof(IgnoredInfoObject, exception), 0, "exception instance"},
    {NULL, 0, 0, 0, NULL}
};

static PyTypeObject IgnoredInfoType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    /* tp_name */       "errortools_speedbelt._ignore_speed.IgnoredInfo",
    /* tp_basicsize */  sizeof(IgnoredInfoObject),
    /* tp_itemsize */   0,
    /* tp_dealloc */    (destructor)IgnoredInfo_dealloc,
    /* tp_print */      0,
    /* tp_getattr */    0,
    /* tp_setattr */    0,
    /* tp_as_async */   0,
    /* tp_repr */       0,
    /* tp_as_number */  0,
    /* tp_as_sequence */0,
    /* tp_as_mapping */ 0,
    /* tp_hash */       0,
    /* tp_call */       0,
    /* tp_str */        0,
    /* tp_getattro */   0,
    /* tp_setattro */   0,
    /* tp_as_buffer */  0,
    /* tp_flags */      Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    /* tp_doc */        0,
    /* tp_traverse */   0,
    /* tp_clear */      0,
    /* tp_richcompare */0,
    /* tp_weaklistoffset */ 0,
    /* tp_iter */       0,
    /* tp_iternext */   0,
    /* tp_methods */    IgnoredInfo_methods,
    /* tp_members */    IgnoredInfo_members,
    /* tp_getset */     0,
    /* tp_base */       0,
    /* tp_dict */       0,
    /* tp_descr_get */  0,
    /* tp_descr_set */  0,
    /* tp_dictoffset */ 0,
    /* tp_init */       (initproc)IgnoredInfo_init,
    /* tp_alloc */      0,
    /* tp_new */        IgnoredInfo_new,
};

/* --- Helpers ------------------------------------------------------------- */

static inline int
identity_match(PyObject *typ, PyObject *excs)
{
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
    return -1;
}

/* --- check_and_record ---------------------------------------------------- */

static PyObject *
check_and_record(PyObject *self, PyObject *const *args, Py_ssize_t nargs)
{
    (void)self;
    if (nargs != 5) {
        PyErr_Format(PyExc_TypeError,
                     "check_and_record() takes exactly 5 arguments (%zd given)",
                     nargs);
        return NULL;
    }

    PyObject *typ = args[0];
    PyObject *val = args[1];
    PyObject *tb = args[2];
    PyObject *info = args[3];
    PyObject *excs = args[4];

    if (IGNORE_IS_NONE(typ)) {
        Py_RETURN_FALSE;
    }

    if (!PyType_Check(typ)) {
        Py_RETURN_FALSE;
    }

    int fast = identity_match(typ, excs);
    if (fast == 0 && PyTuple_Check(excs) && PyTuple_GET_SIZE(excs) == 0) {
        Py_RETURN_FALSE;
    }
    if (fast != 1) {
        int res = PyObject_IsSubclass(typ, excs);
        if (res == -1) {
            return NULL;
        }
        if (!res) {
            Py_RETURN_FALSE;
        }
    }

    if (!PyObject_TypeCheck(info, &IgnoredInfoType)) {
        PyErr_SetString(PyExc_TypeError, "info must be an IgnoredInfo instance");
        return NULL;
    }
    IgnoredInfoObject *info_obj = (IgnoredInfoObject*)info;

    PyObject *name = PyObject_GetAttrString(typ, "__name__");
    if (name == NULL) {
        return NULL;
    }
    Py_XDECREF(info_obj->name);
    info_obj->name = name;

    info_obj->be_ignore = 1;
    info_obj->count += 1;

    /* Build traceback string via traceback module. */
    PyObject *traceback_mod = PyImport_ImportModule("traceback");
    if (traceback_mod == NULL) {
        return NULL;
    }
    PyObject *format_exc = PyObject_GetAttrString(traceback_mod, "format_exception");
    Py_DECREF(traceback_mod);
    if (format_exc == NULL) {
        return NULL;
    }
    PyObject *tb_list = PyObject_CallFunctionObjArgs(format_exc, typ, val, tb, NULL);
    Py_DECREF(format_exc);
    if (tb_list == NULL) {
        return NULL;
    }
    PyObject *sep = PyUnicode_FromString("");
    PyObject *tb_str = PyUnicode_Join(sep, tb_list);
    Py_DECREF(sep);
    Py_DECREF(tb_list);
    if (tb_str == NULL) {
        return NULL;
    }
    Py_XDECREF(info_obj->traceback);
    info_obj->traceback = tb_str;

    Py_XDECREF(info_obj->exception);
    info_obj->exception = val;
    Py_XINCREF(val);

    Py_RETURN_TRUE;
}

/* --- Module definition --------------------------------------------------- */

static PyMethodDef IgnoreSpeedMethods[] = {
    {"check_and_record",
     (PyCFunction)(void (*)(void))check_and_record,
     METH_FASTCALL,
     "check_and_record(typ, val, tb, info, excs) -> bool\n\n"
     "Fast-path for ErrorIgnoreWrapper.__exit__."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef ignore_speed_module = {
    PyModuleDef_HEAD_INIT,
    /* m_name */   "_ignore_speed",
    /* m_doc */    "C speedup for errortools ignore wrapper.",
    /* m_size */   0,
    /* m_methods */IgnoreSpeedMethods,
    /* m_slots */  NULL,
    /* m_traverse */NULL,
    /* m_clear */  NULL,
    /* m_free */   NULL,
};

PyMODINIT_FUNC
PyInit__ignore_speed(void)
{
    PyObject *m = PyModule_Create(&ignore_speed_module);
    if (m == NULL) {
        return NULL;
    }

    if (PyType_Ready(&IgnoredInfoType) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    Py_INCREF(&IgnoredInfoType);
    if (PyModule_AddObject(m, "IgnoredInfo", (PyObject*)&IgnoredInfoType) < 0) {
        Py_DECREF(&IgnoredInfoType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
