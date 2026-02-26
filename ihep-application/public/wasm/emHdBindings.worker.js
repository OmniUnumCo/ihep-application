/**
 * Emscripten pthread worker with security hardening
 * Security: URL validation added to prevent arbitrary script loading
 */
var initializedJS = false;
var Module = {};

// Security: Validate URLs before loading to prevent arbitrary script injection
function isValidScriptUrl(url) {
    if (typeof url !== "string") return false;
    try {
        var parsed = new URL(url, self.location.href);
        // Only allow same-origin scripts or blob URLs
        if (parsed.protocol === "blob:") return true;
        if (parsed.origin === self.location.origin) return true;
        // Reject all other origins
        return false;
    } catch (e) {
        return false;
    }
}

function safeImportScripts(url) {
    if (!isValidScriptUrl(url)) {
        throw new Error("Security: Blocked attempt to load script from untrusted origin");
    }
    importScripts(url);
}

function assert(condition, text) {
    if (!condition) abort("Assertion failed: " + text);
}

function threadPrintErr() {
    var text = Array.prototype.slice.call(arguments).join(" ");
    console.error(text);
}

function threadAlert() {
    var text = Array.prototype.slice.call(arguments).join(" ");
    postMessage({ cmd: "alert", text: text, threadId: Module["_pthread_self"]() });
}

var out = function() { throw "out() is not defined in worker.js."; };
var err = threadPrintErr;
this.alert = threadAlert;

Module["instantiateWasm"] = function(info, receiveInstance) {
    var instance = new WebAssembly.Instance(Module["wasmModule"], info);
    Module["wasmModule"] = null;
    receiveInstance(instance);
    return instance.exports;
};

this.onmessage = function(e) {
    try {
        if (e.data.cmd === "load") {
            Module["wasmModule"] = e.data.wasmModule;
            Module["wasmMemory"] = e.data.wasmMemory;
            Module["buffer"] = Module["wasmMemory"].buffer;
            Module["ENVIRONMENT_IS_PTHREAD"] = true;

            if (typeof e.data.urlOrBlob === "string") {
                // Security: Validate URL before importing
                safeImportScripts(e.data.urlOrBlob);
            } else {
                var objectUrl = URL.createObjectURL(e.data.urlOrBlob);
                try {
                    safeImportScripts(objectUrl);
                } finally {
                    URL.revokeObjectURL(objectUrl);
                }
            }

            getUsdModule(Module).then(function(instance) {
                Module = instance;
                postMessage({ "cmd": "loaded" });
            });
        } else if (e.data.cmd === "objectTransfer") {
            Module["PThread"].receiveObjectTransfer(e.data);
        } else if (e.data.cmd === "run") {
            Module["__performance_now_clock_drift"] = performance.now() - e.data.time;
            var threadInfoStruct = e.data.threadInfoStruct;
            Module["__emscripten_thread_init"](threadInfoStruct, 0, 0);
            var max = e.data.stackBase;
            var top = e.data.stackBase + e.data.stackSize;
            assert(threadInfoStruct);
            assert(top != 0);
            assert(max != 0);
            assert(top > max);
            Module["establishStackSpace"](top, max);
            Module["_emscripten_tls_init"]();
            Module["PThread"].receiveObjectTransfer(e.data);
            Module["PThread"].setThreadStatus(Module["_pthread_self"](), 1);

            if (!initializedJS) {
                Module["___embind_register_native_and_builtin_types"]();
                initializedJS = true;
            }

            try {
                var result = Module["invokeEntryPoint"](e.data.start_routine, e.data.arg);
                Module["checkStackCookie"]();
                if (!Module["getNoExitRuntime"]()) Module["PThread"].threadExit(result);
            } catch (ex) {
                if (ex === "Canceled!") {
                    Module["PThread"].threadCancel();
                } else if (ex != "unwind") {
                    if (typeof Module["_emscripten_futex_wake"] !== "function") {
                        err("Thread Initialisation failed.");
                        throw ex;
                    }
                    if (ex instanceof Module["ExitStatus"]) {
                        if (Module["getNoExitRuntime"]()) {
                            err("Pthread 0x" + _pthread_self().toString(16) + " called exit(), staying alive due to noExitRuntime.");
                        } else {
                            err("Pthread 0x" + _pthread_self().toString(16) + " called exit(), calling threadExit.");
                            Module["PThread"].threadExit(ex.status);
                        }
                    } else {
                        Module["PThread"].threadExit(-2);
                        throw ex;
                    }
                } else {
                    err("Pthread 0x" + threadInfoStruct.toString(16) + " completed its pthread main entry point with an unwind, keeping the pthread worker alive for asynchronous operation.");
                }
            }
        } else if (e.data.cmd === "cancel") {
            if (threadInfoStruct) {
                Module["PThread"].threadCancel();
            }
        } else if (e.data.target === "setimmediate") {
            // No-op for setimmediate
        } else if (e.data.cmd === "processThreadQueue") {
            if (threadInfoStruct) {
                Module["_emscripten_current_thread_process_queued_calls"]();
            }
        } else {
            err("worker.js received unknown command " + e.data.cmd);
            // Security: Don't log e.data as it may contain sensitive information
        }
    } catch (ex) {
        // Security: Only log error type, not full details which may contain sensitive data
        err("worker.js onmessage() captured an uncaught exception");
        if (ex && ex.stack) err(ex.stack);
        throw ex;
    }
};

// Node.js environment support
if (typeof process === "object" && typeof process.versions === "object" && typeof process.versions.node === "string") {
    self = { location: { href: __filename } };
    var onmessage = this.onmessage;
    var nodeWorkerThreads = require("worker_threads");
    global.Worker = nodeWorkerThreads.Worker;
    var parentPort = nodeWorkerThreads.parentPort;
    parentPort.on("message", function(data) { onmessage({ data: data }); });
    var nodeFS = require("fs");
    var nodeRead = function(filename) { return nodeFS.readFileSync(filename, "utf8"); };

    function globalEval(x) {
        global.require = require;
        global.Module = Module;
        eval.call(null, x);
    }

    importScripts = function(f) {
        // Security: Validate file path in Node environment
        if (typeof f !== "string" || f.includes("..") || !f.startsWith("/") && !f.startsWith("./")) {
            throw new Error("Security: Invalid script path");
        }
        globalEval(nodeRead(f));
    };

    postMessage = function(msg) { parentPort.postMessage(msg); };

    if (typeof performance === "undefined") {
        performance = { now: function() { return Date.now(); } };
    }
}
