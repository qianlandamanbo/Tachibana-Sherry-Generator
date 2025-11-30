#include <Python.h>
#include <windows.h>
#include <imm.h> 

#define WH_KEYBOARD_LL 13
#define WM_KEYDOWN 0x0100
#define WM_KEYUP 0x0101
#define WM_SYSKEYDOWN 0x0104
#define WM_SYSKEYUP 0x0105

// Global variables
static HHOOK g_hook = NULL;
static PyObject* g_callback = NULL;
static HMODULE g_hModule = NULL;
static int g_hotkey_mode = 0; // 0=enter, 1=ctrl+enter
static int g_ctrl_pressed = 0; // Track Ctrl key state


int is_ime_composing() {
    HWND hwnd = GetForegroundWindow();
    if (!hwnd) return 0;
    
    HIMC himc = ImmGetContext(hwnd);
    if (!himc) return 0;
    
    
    DWORD dwConversion, dwSentence;
    BOOL has_composition = FALSE;
    
    if (ImmGetConversionStatus(himc, &dwConversion, &dwSentence)) {
        
        LONG composition_len = ImmGetCompositionString(himc, GCS_COMPSTR, NULL, 0);
        has_composition = (composition_len > 0);
    }
    
    ImmReleaseContext(hwnd, himc);
    return has_composition;
}

// Keyboard hook callback function
LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode >= 0) {
        KBDLLHOOKSTRUCT* kbStruct = (KBDLLHOOKSTRUCT*)lParam;
        int vk_code = kbStruct->vkCode;
        
        // Track Ctrl key state
        if (vk_code == VK_CONTROL || vk_code == VK_LCONTROL || vk_code == VK_RCONTROL) {
            if (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN) {
                g_ctrl_pressed = 1;
            } else if (wParam == WM_KEYUP || wParam == WM_SYSKEYUP) {
                g_ctrl_pressed = 0;
            }
        }
        
        // Process key down events for Enter key
        if ((wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN) && vk_code == VK_RETURN) {
            int should_block = 0;
            
            
            if (is_ime_composing()) {
                
                should_block = 0;
            } else {
                if (g_hotkey_mode == 0) {
                    // Enter mode - block all Enter keys
                    should_block = 1;
                } else if (g_hotkey_mode == 1) {
                    // Ctrl+Enter mode - check if Ctrl is pressed
                    if (g_ctrl_pressed) {
                        should_block = 1;
                    }
                }
            }
            
            if (should_block && g_callback != NULL) {
                // Block the key and call callback
                PyGILState_STATE gstate;
                gstate = PyGILState_Ensure();
                
                PyObject* arglist = Py_BuildValue("(i)", vk_code);
                PyObject* result = PyObject_CallObject(g_callback, arglist);
                Py_XDECREF(arglist);
                Py_XDECREF(result);
                
                PyGILState_Release(gstate);
                
                return 1; // Block the key completely
            }
        }
    }
    
    return CallNextHookEx(g_hook, nCode, wParam, lParam);
}

// Set keyboard hook with hotkey mode
static PyObject* set_keyboard_hook(PyObject* self, PyObject* args) {
    PyObject* callback;
    int hotkey_mode;
    
    if (!PyArg_ParseTuple(args, "Oi", &callback, &hotkey_mode)) {
        return NULL;
    }
    
    // Check if callback is callable
    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError, "Parameter must be callable");
        return NULL;
    }
    
    // Clean up previous hook
    if (g_hook != NULL) {
        UnhookWindowsHookEx(g_hook);
        g_hook = NULL;
    }
    
    // Reset state
    g_ctrl_pressed = 0;
    
    // Save callback reference and hotkey mode
    Py_XDECREF(g_callback);
    g_callback = callback;
    Py_INCREF(g_callback);
    g_hotkey_mode = hotkey_mode;
    
    // Set keyboard hook
    g_hook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, g_hModule, 0);
    
    if (g_hook == NULL) {
        DWORD error = GetLastError();
        Py_XDECREF(g_callback);
        g_callback = NULL;
        PyErr_SetString(PyExc_OSError, "Failed to set keyboard hook");
        return NULL;
    }
    
    Py_RETURN_TRUE;
}

// Remove keyboard hook
static PyObject* remove_keyboard_hook(PyObject* self, PyObject* args) {
    if (g_hook != NULL) {
        UnhookWindowsHookEx(g_hook);
        g_hook = NULL;
    }
    
    Py_XDECREF(g_callback);
    g_callback = NULL;
    g_ctrl_pressed = 0;
    
    Py_RETURN_TRUE;
}

// Check hook status
static PyObject* is_hook_active(PyObject* self, PyObject* args) {
    if (g_hook != NULL) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

// Module method definitions
static PyMethodDef KeyboardHookMethods[] = {
    {"set_keyboard_hook", set_keyboard_hook, METH_VARARGS, "Set keyboard hook"},
    {"remove_keyboard_hook", remove_keyboard_hook, METH_VARARGS, "Remove keyboard hook"},
    {"is_hook_active", is_hook_active, METH_VARARGS, "Check hook status"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef keyboardhookmodule = {
    PyModuleDef_HEAD_INIT,
    "keyboardhook",
    "Keyboard hook module",
    -1,
    KeyboardHookMethods
};

// Module initialization function
PyMODINIT_FUNC PyInit_keyboardhook(void) {
    g_hModule = GetModuleHandle(NULL);
    return PyModule_Create(&keyboardhookmodule);
}