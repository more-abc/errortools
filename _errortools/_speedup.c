#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* Fast exception type checking */
static PyObject* fast_issubclass_check(PyObject* self, PyObject* args) {
    PyObject *typ, *excs;
    if (!PyArg_ParseTuple(args, "OO", &typ, &excs)) {
        return NULL;
    }

    if (typ == Py_None) {
        Py_RETURN_FALSE;
    }

    int result = PyObject_IsSubclass(typ, excs);
    if (result == -1) {
        return NULL;
    }

    return PyBool_FromLong(result);
}

/* Fast exception collector append */
static PyObject* fast_append_exception(PyObject* self, PyObject* args) {
    PyObject *list, *exc;
    if (!PyArg_ParseTuple(args, "OO", &list, &exc)) {
        return NULL;
    }

    if (PyList_Append(list, exc) == -1) {
        return NULL;
    }

    Py_RETURN_NONE;
}

/* Method definitions */
static PyMethodDef SpeedupMethods[] = {
    {"fast_issubclass_check", fast_issubclass_check, METH_VARARGS,
     "Fast exception type checking"},
    {"fast_append_exception", fast_append_exception, METH_VARARGS,
     "Fast exception list append"},
    {NULL, NULL, 0, NULL}
};

/* Module definition */
static struct PyModuleDef speedupmodule = {
    PyModuleDef_HEAD_INIT,
    "_speedup",
    "C speedup for errortools",
    -1,
    SpeedupMethods
};

/* Module initialization */
PyMODINIT_FUNC PyInit__speedup(void) {
    return PyModule_Create(&speedupmodule);
}
