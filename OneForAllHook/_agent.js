(function(){function r(e,n,t){function o(i,f){if(!n[i]){if(!e[i]){var c="function"==typeof require&&require;if(!f&&c)return c(i,!0);if(u)return u(i,!0);var a=new Error("Cannot find module '"+i+"'");throw a.code="MODULE_NOT_FOUND",a}var p=n[i]={exports:{}};e[i][0].call(p.exports,function(r){var n=e[i][1][r];return o(n||r)},p,p.exports,r,e,n,t)}return n[i].exports}for(var u="function"==typeof require&&require,i=0;i<t.length;i++)o(t[i]);return o}return r})()({1:[function(require,module,exports){
"use strict";

var _interopRequireDefault = require("@babel/runtime-corejs2/helpers/interopRequireDefault");

var _stringify = _interopRequireDefault(require("@babel/runtime-corejs2/core-js/json/stringify"));

var _defineProperty = _interopRequireDefault(require("@babel/runtime-corejs2/core-js/object/define-property"));

(0, _defineProperty["default"])(exports, "__esModule", {
  value: true
});
exports.hooking = void 0;

var color_1 = require("../lib/color");

var hooking;

(function (hooking) {
  function get_class_method_names(clazz_instance) {
    try {
      if (typeof clazz_instance == 'string') {
        clazz_instance = Java.use(clazz_instance);
      }

      var method_names = clazz_instance["class"].getDeclaredMethods().filter(function (method) {
        if (method.getName().indexOf("-") == 0) {
          return false;
        }

        return true;
      }).map(function (method) {
        // let m: string = method.toGenericString();
        // while (m.includes("<")) { m = m.replace(/<.*?>/g, ""); }
        // if (m.indexOf(" throws ") !== -1) { m = m.substring(0, m.indexOf(" throws ")); }
        // m = m.slice(m.lastIndexOf(" "));
        // m = m.replace(` ${clazz_instance.class.getName()}.`, "");
        // return m.split("(")[0];
        return method.getName();
      }).filter(function (value, index, self) {
        return self.indexOf(value) === index;
      });
      return method_names;
    } catch (e) {
      return [];
    }
  }

  hooking.get_class_method_names = get_class_method_names;

  function hook_method_implementation(def_class, method_implementation, trace_flag, arg_val_flag) {
    var class_name = def_class;
    var method_name = method_implementation.methodName;
    var args = method_implementation.argumentTypes.map(function (arg) {
      return arg.className;
    });
    var args_type = args.join(',');
    var return_type = method_implementation.returnType.className;
    console.log("[+] Hooking ".concat(color_1.colors.green(class_name), ".").concat(color_1.colors.greenBright(method_name), "(").concat(color_1.colors.red(args_type), ")"));
    var throwable = Java.use("java.lang.Throwable");

    method_implementation.implementation = function () {
      console.log("[+] Call ".concat(color_1.colors.green(class_name), ".").concat(color_1.colors.greenBright(method_name), "(").concat(color_1.colors.red(args_type), ")"));
      var report = {};
      report['callee'] = class_name + '.' + method_name;
      report['argTypes'] = args_type;
      report['retType'] = return_type;

      if (trace_flag) {
        report['backtrace'] = throwable.$new().getStackTrace().map(function (trace_element) {
          return trace_element.toString() + "\n\t";
        }).join("");
      }

      if (arg_val_flag) {
        report['argVals'] = arguments;
      }

      send((0, _stringify["default"])(report, null)); // actually run the intended method

      return method_implementation.apply(this, arguments);
    };
  }

  function hook_class_methods(clazz, trace_flag, arg_val_flag) {
    try {
      var clazz_instance = Java.use(clazz);
      var simple_method_names = get_class_method_names(clazz_instance);
      simple_method_names.forEach(function (name) {
        // 这里的method类型和getDeclaredMethods()方法拿到的method不一样，注意区分两个的差异
        clazz_instance[name].overloads.forEach(function (method) {
          hook_method_implementation(clazz, method, trace_flag, arg_val_flag);
        });
      });
    } catch (e) {}
  }

  hooking.hook_class_methods = hook_class_methods;

  function hook_target_method(clazz, method_name, arg_types, return_types, trace_flag, arg_val_flag) {
    try {
      var clazz_instance = Java.use(clazz);
      clazz_instance[method_name].overloads.forEach(function (method) {
        var same_flag = true;
        var args_string = method.argumentTypes.map(function (arg) {
          return arg.className;
        }).join(','); //空入参的target方法入参写 ‘void’

        if (args_string == '') {
          args_string = 'void';
        }

        var return_string = method.returnType.className.toString();

        if (arg_types != '' && arg_types != args_string) {
          same_flag = false;
        }

        if (return_types != '' && return_types != return_string) {
          same_flag = false;
        }

        if (same_flag) {
          hook_method_implementation(clazz, method, trace_flag, arg_val_flag);
        }
      });
    } catch (e) {
      console.log('no target class');
    }
  }

  hooking.hook_target_method = hook_target_method;
})(hooking = exports.hooking || (exports.hooking = {}));

},{"../lib/color":4,"@babel/runtime-corejs2/core-js/json/stringify":5,"@babel/runtime-corejs2/core-js/object/define-property":6,"@babel/runtime-corejs2/helpers/interopRequireDefault":7}],2:[function(require,module,exports){
"use strict";

var _interopRequireDefault = require("@babel/runtime-corejs2/helpers/interopRequireDefault");

var _defineProperty = _interopRequireDefault(require("@babel/runtime-corejs2/core-js/object/define-property"));

(0, _defineProperty["default"])(exports, "__esModule", {
  value: true
});

var scenario_1 = require("./scenario");

Java.performNow(function () {
  if (Java.available) {
    console.log('[+] JVM load success');
    scenario_1.locationReleatedHook(true, false);
    scenario_1.cameraReleatedHook(true, true);
    scenario_1.audioReleatedHook(true, true);
    scenario_1.mircophoneReleatedHook(true, true);
    scenario_1.contactReleatedHook(true, true);
    scenario_1.smsReleatedHook(true, true);
    scenario_1.life_cycle_hook(false, false);
    scenario_1.permission_request_hook(true, false); // test_func();
  }
});
Java.perform(function () {
  if (Java.available) {
    console.log('[+] JVM load success');
    scenario_1.ad_hook();
  }
});

},{"./scenario":3,"@babel/runtime-corejs2/core-js/object/define-property":6,"@babel/runtime-corejs2/helpers/interopRequireDefault":7}],3:[function(require,module,exports){
"use strict";

var _interopRequireDefault = require("@babel/runtime-corejs2/helpers/interopRequireDefault");

var _defineProperty = _interopRequireDefault(require("@babel/runtime-corejs2/core-js/object/define-property"));

(0, _defineProperty["default"])(exports, "__esModule", {
  value: true
});
exports.test_func = exports.ad_hook = exports.permission_request_hook = exports.life_cycle_hook = exports.smsReleatedHook = exports.contactReleatedHook = exports.mircophoneReleatedHook = exports.audioReleatedHook = exports.locationReleatedHook = exports.cameraReleatedHook = void 0;

var hook_1 = require("./hook");

function cameraReleatedHook(trace_flag, arg_vals) {
  var target_classes;
  target_classes = ['android.hardware.Camera', 'android.hardware.camera2.CameraManager', 'android.hardware.camera2.CaptureResult', 'android.hardware.camera2.CaptureRequest', 'android.hardware.camera2.impl.CameraDeviceImpl'];
  target_classes.forEach(function (clazz) {
    hook_1.hooking.hook_class_methods(clazz, trace_flag, arg_vals);
  });
}

exports.cameraReleatedHook = cameraReleatedHook;

function locationReleatedHook(trace_flag, arg_vals) {
  var target_classes;
  target_classes = ["android.location.GpsStatus$SatelliteIterator", "android.location.IGnssStatusListener$Stub", "android.location.GpsStatus$SatelliteIterator", "android.location.LocationManager$GnssStatusListenerTransport$GnssHandler", "android.location.LocationManager$GnssStatusListenerTransport", "android.location.GpsSatellite", "android.location.LocationManager", "android.location.GpsStatus", "android.location.GpsStatus$1", "android.location.Location"];
  target_classes.forEach(function (clazz) {
    hook_1.hooking.hook_class_methods(clazz, trace_flag, arg_vals);
  });
}

exports.locationReleatedHook = locationReleatedHook;

function audioReleatedHook(trace_flag, arg_vals) {
  var target_classes;
  target_classes = ['android.media.MediaPlayer', 'android.media.MediaPlayer$TimeProvider', 'android.media.AudioTrack', 'android.media.PlayerBase', 'android.speech.tts.TextToSpeech', 'android.media.SoundPool'];
  target_classes.forEach(function (clazz) {
    hook_1.hooking.hook_class_methods(clazz, trace_flag, arg_vals);
  });
}

exports.audioReleatedHook = audioReleatedHook;

function mircophoneReleatedHook(trace_flag, arg_vals) {
  var target_classes;
  target_classes = ['android.media.AudioRecord', 'android.media.AudioManager', 'android.media.MediaRecorder'];
  target_classes.forEach(function (clazz) {
    hook_1.hooking.hook_class_methods(clazz, trace_flag, arg_vals);
  });
}

exports.mircophoneReleatedHook = mircophoneReleatedHook;

function contactReleatedHook(trace_flag, arg_vals) {
  var target_classes;
  target_classes = ['android.provider.ContactsContract', 'android.provider.ContactsContract$RawContacts', 'android.content.ContentResolver'];
  target_classes.forEach(function (clazz) {
    hook_1.hooking.hook_class_methods(clazz, trace_flag, arg_vals);
  }); // android.net.Uri 调用地点比较多，主要hook parse方法

  hook_1.hooking.hook_target_method('android.net.Uri', 'parse', '', '', trace_flag, arg_vals);
}

exports.contactReleatedHook = contactReleatedHook;

function smsReleatedHook(trace_flag, arg_vals) {
  var target_classes; // android.provider.Telephony.Sms见的比较少，大多数直接查询
  // 读取短信也是查询数据库和contact类似，但是sms数据库中有date信息，通常读取时会格式化时间戳，调用太频繁了

  target_classes = [// 'android.icu.text.SimpleDateFormat',
  // 'java.text.SimpleDateFormat',
  'android.provider.Telephony$Sms', 'android.provider.Telephony$Mms', 'android.provider.Telephony', 'android.telephony.TelephonyManager'];
  target_classes.forEach(function (clazz) {
    hook_1.hooking.hook_class_methods(clazz, trace_flag, arg_vals);
  });
}

exports.smsReleatedHook = smsReleatedHook;

function life_cycle_hook(trace_flag, arg_vals) {
  var target_classes;
  target_classes = ['android.app.Activity', 'android.app.Service'];
  target_classes.forEach(function (clazz) {
    hook_1.hooking.hook_target_method(clazz, 'onCreate', '', '', trace_flag, arg_vals);
  });
}

exports.life_cycle_hook = life_cycle_hook;

function permission_request_hook(trace_flag, arg_vals) {
  hook_1.hooking.hook_target_method('android.app.Activity', 'requestPermissions', '', '', trace_flag, arg_vals);
  hook_1.hooking.hook_target_method('android.app.Fragment', 'requestPermissions', '', '', trace_flag, arg_vals);
}

exports.permission_request_hook = permission_request_hook;

function ad_hook() {
  var google_target_classes = ['com.google.android.gms.ads.AdRequest$Builder', 'com.google.android.gms.ads.doubleclick.PublisherAdRequest$Builder', 'com.google.android.gms.ads.search.SearchAdRequest$Builder', // 特殊混淆情况
  'com.google.android.gms.ads.c$a', 'com.google.android.gms.ads.d$a'];
  google_target_classes.forEach(function (google_target_class) {
    hook_1.hooking.get_class_method_names(google_target_class).forEach(function (method) {
      hook_1.hooking.hook_target_method(google_target_class, method, 'android.location.Location', '', true, false);

      if (method == 'setGender' || method == 'setBirthday') {
        hook_1.hooking.hook_target_method(google_target_class, method, '', '', true, false);
      }
    });
  }); // facebook 没找到地理位置接口
  // let fb_target_class = ''

  var mopub_target_class = 'com.mopub.common.AdUrlGenerator';
  hook_1.hooking.get_class_method_names(mopub_target_class).forEach(function (method) {
    hook_1.hooking.hook_target_method(mopub_target_class, method, 'android.location.Location', 'void', true, false);
  }); //旧版本Mopub没有带参数的setLocation方法，可以用旧版本的getLastKnownLocation判断，和新版本的不同

  var mopub_target_class_old = 'com.mopub.common.LocationService';
  hook_1.hooking.get_class_method_names(mopub_target_class_old).forEach(function (method) {
    hook_1.hooking.hook_target_method(mopub_target_class_old, method, 'android.content.Context', 'android.location.Location', true, false);
  });
  var amazon_target_classes = ['com.amazon.device.ads.AdLocation', 'com.amazon.device.ads.DtbGeoLocation'];
  amazon_target_classes.forEach(function (amazon_target_class) {
    hook_1.hooking.get_class_method_names(amazon_target_class).forEach(function (method) {
      hook_1.hooking.hook_target_method(amazon_target_class, method, 'void', 'android.location.Location', true, false);
    });
  }); // flurry本身sdk就已经混淆了

  var flurry_target_class = 'com.flurry.sdk.ads.cf';
  hook_1.hooking.get_class_method_names(flurry_target_class).forEach(function (method) {
    hook_1.hooking.hook_target_method(flurry_target_class, method, '', 'android.location.Location', true, false);
  });
  var inmobi_target_class = 'com.inmobi.sdk.InMobiSdk';
  hook_1.hooking.get_class_method_names(inmobi_target_class).forEach(function (method) {
    hook_1.hooking.hook_target_method(inmobi_target_class, method, 'android.location.Location', '', true, false); //setLocationWithCityStateCountry

    hook_1.hooking.hook_target_method(inmobi_target_class, method, 'java.lang.String,java.lang.String,java.lang.String', '', true, false);
  });
  var adcolony_target_class = 'com.adcolony.sdk.AdColonyUserMetadata';
  hook_1.hooking.get_class_method_names(adcolony_target_class).forEach(function (method) {
    hook_1.hooking.hook_target_method(adcolony_target_class, method, 'android.location.Location', '', true, false);

    if (method == 'setUserGender' || method == 'setUserAge') {
      hook_1.hooking.hook_target_method(adcolony_target_class, method, '', '', true, false);
    }
  }); // appLovin sdk类名混淆，并且本身用的好像是WebSettings的setGeolocationEnabled
  // let appLovin_target_class = ''
  // appodeal sdk类名混淆，并且用的比较少 都是bm

  var appodeal_target_class = 'com.appodeal.ads.bm';
  hook_1.hooking.get_class_method_names(appodeal_target_class).forEach(function (method) {
    hook_1.hooking.hook_target_method(appodeal_target_class, method, '', 'android.location.Location', true, false);
  });
}

exports.ad_hook = ad_hook;

function test_func() {
  hook_1.hooking.hook_target_method('android.location.Location', 'distanceBetween', '', '', true, true);
}

exports.test_func = test_func;

},{"./hook":1,"@babel/runtime-corejs2/core-js/object/define-property":6,"@babel/runtime-corejs2/helpers/interopRequireDefault":7}],4:[function(require,module,exports){
"use strict";

var _interopRequireDefault = require("@babel/runtime-corejs2/helpers/interopRequireDefault");

var _defineProperty = _interopRequireDefault(require("@babel/runtime-corejs2/core-js/object/define-property"));

(0, _defineProperty["default"])(exports, "__esModule", {
  value: true
});
exports.colors = void 0;
var colors;

(function (colors) {
  var base = "\x1B[%dm";
  var reset = "\x1B[39m";

  colors.black = function (message) {
    return colors.ansify(30, message);
  };

  colors.blue = function (message) {
    return colors.ansify(34, message);
  };

  colors.cyan = function (message) {
    return colors.ansify(36, message);
  };

  colors.green = function (message) {
    return colors.ansify(32, message);
  };

  colors.magenta = function (message) {
    return colors.ansify(35, message);
  };

  colors.red = function (message) {
    return colors.ansify(31, message);
  };

  colors.white = function (message) {
    return colors.ansify(37, message);
  };

  colors.yellow = function (message) {
    return colors.ansify(33, message);
  };

  colors.blackBright = function (message) {
    return colors.ansify(90, message);
  };

  colors.redBright = function (message) {
    return colors.ansify(91, message);
  };

  colors.greenBright = function (message) {
    return colors.ansify(92, message);
  };

  colors.yellowBright = function (message) {
    return colors.ansify(93, message);
  };

  colors.blueBright = function (message) {
    return colors.ansify(94, message);
  };

  colors.cyanBright = function (message) {
    return colors.ansify(96, message);
  };

  colors.whiteBright = function (message) {
    return colors.ansify(97, message);
  }; // return an ansified string


  colors.ansify = function (color) {
    for (var _len = arguments.length, msg = new Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {
      msg[_key - 1] = arguments[_key];
    }

    return base.replace("%d", color.toString()) + msg.join("") + reset;
  }; // tslint:disable-next-line:no-eval


  colors.clog = function (color) {
    for (var _len2 = arguments.length, msg = new Array(_len2 > 1 ? _len2 - 1 : 0), _key2 = 1; _key2 < _len2; _key2++) {
      msg[_key2 - 1] = arguments[_key2];
    }

    return eval("console").log(colors.ansify.apply(colors, [color].concat(msg)));
  }; // tslint:disable-next-line:no-eval


  colors.log = function () {
    for (var _len3 = arguments.length, msg = new Array(_len3), _key3 = 0; _key3 < _len3; _key3++) {
      msg[_key3] = arguments[_key3];
    }

    return eval("console").log(msg.join(""));
  }; // log based on a quiet flag


  colors.qlog = function (quiet) {
    if (quiet === false) {
      for (var _len4 = arguments.length, msg = new Array(_len4 > 1 ? _len4 - 1 : 0), _key4 = 1; _key4 < _len4; _key4++) {
        msg[_key4 - 1] = arguments[_key4];
      }

      colors.log.apply(colors, msg);
    }
  };
})(colors = exports.colors || (exports.colors = {}));

},{"@babel/runtime-corejs2/core-js/object/define-property":6,"@babel/runtime-corejs2/helpers/interopRequireDefault":7}],5:[function(require,module,exports){
module.exports = require("core-js/library/fn/json/stringify");
},{"core-js/library/fn/json/stringify":8}],6:[function(require,module,exports){
module.exports = require("core-js/library/fn/object/define-property");
},{"core-js/library/fn/object/define-property":9}],7:[function(require,module,exports){
function _interopRequireDefault(obj) {
  return obj && obj.__esModule ? obj : {
    "default": obj
  };
}

module.exports = _interopRequireDefault;
},{}],8:[function(require,module,exports){
var core = require('../../modules/_core');
var $JSON = core.JSON || (core.JSON = { stringify: JSON.stringify });
module.exports = function stringify(it) { // eslint-disable-line no-unused-vars
  return $JSON.stringify.apply($JSON, arguments);
};

},{"../../modules/_core":12}],9:[function(require,module,exports){
require('../../modules/es6.object.define-property');
var $Object = require('../../modules/_core').Object;
module.exports = function defineProperty(it, key, desc) {
  return $Object.defineProperty(it, key, desc);
};

},{"../../modules/_core":12,"../../modules/es6.object.define-property":26}],10:[function(require,module,exports){
module.exports = function (it) {
  if (typeof it != 'function') throw TypeError(it + ' is not a function!');
  return it;
};

},{}],11:[function(require,module,exports){
var isObject = require('./_is-object');
module.exports = function (it) {
  if (!isObject(it)) throw TypeError(it + ' is not an object!');
  return it;
};

},{"./_is-object":22}],12:[function(require,module,exports){
var core = module.exports = { version: '2.6.11' };
if (typeof __e == 'number') __e = core; // eslint-disable-line no-undef

},{}],13:[function(require,module,exports){
// optional / simple context binding
var aFunction = require('./_a-function');
module.exports = function (fn, that, length) {
  aFunction(fn);
  if (that === undefined) return fn;
  switch (length) {
    case 1: return function (a) {
      return fn.call(that, a);
    };
    case 2: return function (a, b) {
      return fn.call(that, a, b);
    };
    case 3: return function (a, b, c) {
      return fn.call(that, a, b, c);
    };
  }
  return function (/* ...args */) {
    return fn.apply(that, arguments);
  };
};

},{"./_a-function":10}],14:[function(require,module,exports){
// Thank's IE8 for his funny defineProperty
module.exports = !require('./_fails')(function () {
  return Object.defineProperty({}, 'a', { get: function () { return 7; } }).a != 7;
});

},{"./_fails":17}],15:[function(require,module,exports){
var isObject = require('./_is-object');
var document = require('./_global').document;
// typeof document.createElement is 'object' in old IE
var is = isObject(document) && isObject(document.createElement);
module.exports = function (it) {
  return is ? document.createElement(it) : {};
};

},{"./_global":18,"./_is-object":22}],16:[function(require,module,exports){
var global = require('./_global');
var core = require('./_core');
var ctx = require('./_ctx');
var hide = require('./_hide');
var has = require('./_has');
var PROTOTYPE = 'prototype';

var $export = function (type, name, source) {
  var IS_FORCED = type & $export.F;
  var IS_GLOBAL = type & $export.G;
  var IS_STATIC = type & $export.S;
  var IS_PROTO = type & $export.P;
  var IS_BIND = type & $export.B;
  var IS_WRAP = type & $export.W;
  var exports = IS_GLOBAL ? core : core[name] || (core[name] = {});
  var expProto = exports[PROTOTYPE];
  var target = IS_GLOBAL ? global : IS_STATIC ? global[name] : (global[name] || {})[PROTOTYPE];
  var key, own, out;
  if (IS_GLOBAL) source = name;
  for (key in source) {
    // contains in native
    own = !IS_FORCED && target && target[key] !== undefined;
    if (own && has(exports, key)) continue;
    // export native or passed
    out = own ? target[key] : source[key];
    // prevent global pollution for namespaces
    exports[key] = IS_GLOBAL && typeof target[key] != 'function' ? source[key]
    // bind timers to global for call from export context
    : IS_BIND && own ? ctx(out, global)
    // wrap global constructors for prevent change them in library
    : IS_WRAP && target[key] == out ? (function (C) {
      var F = function (a, b, c) {
        if (this instanceof C) {
          switch (arguments.length) {
            case 0: return new C();
            case 1: return new C(a);
            case 2: return new C(a, b);
          } return new C(a, b, c);
        } return C.apply(this, arguments);
      };
      F[PROTOTYPE] = C[PROTOTYPE];
      return F;
    // make static versions for prototype methods
    })(out) : IS_PROTO && typeof out == 'function' ? ctx(Function.call, out) : out;
    // export proto methods to core.%CONSTRUCTOR%.methods.%NAME%
    if (IS_PROTO) {
      (exports.virtual || (exports.virtual = {}))[key] = out;
      // export proto methods to core.%CONSTRUCTOR%.prototype.%NAME%
      if (type & $export.R && expProto && !expProto[key]) hide(expProto, key, out);
    }
  }
};
// type bitmap
$export.F = 1;   // forced
$export.G = 2;   // global
$export.S = 4;   // static
$export.P = 8;   // proto
$export.B = 16;  // bind
$export.W = 32;  // wrap
$export.U = 64;  // safe
$export.R = 128; // real proto method for `library`
module.exports = $export;

},{"./_core":12,"./_ctx":13,"./_global":18,"./_has":19,"./_hide":20}],17:[function(require,module,exports){
module.exports = function (exec) {
  try {
    return !!exec();
  } catch (e) {
    return true;
  }
};

},{}],18:[function(require,module,exports){
// https://github.com/zloirock/core-js/issues/86#issuecomment-115759028
var global = module.exports = typeof window != 'undefined' && window.Math == Math
  ? window : typeof self != 'undefined' && self.Math == Math ? self
  // eslint-disable-next-line no-new-func
  : Function('return this')();
if (typeof __g == 'number') __g = global; // eslint-disable-line no-undef

},{}],19:[function(require,module,exports){
var hasOwnProperty = {}.hasOwnProperty;
module.exports = function (it, key) {
  return hasOwnProperty.call(it, key);
};

},{}],20:[function(require,module,exports){
var dP = require('./_object-dp');
var createDesc = require('./_property-desc');
module.exports = require('./_descriptors') ? function (object, key, value) {
  return dP.f(object, key, createDesc(1, value));
} : function (object, key, value) {
  object[key] = value;
  return object;
};

},{"./_descriptors":14,"./_object-dp":23,"./_property-desc":24}],21:[function(require,module,exports){
module.exports = !require('./_descriptors') && !require('./_fails')(function () {
  return Object.defineProperty(require('./_dom-create')('div'), 'a', { get: function () { return 7; } }).a != 7;
});

},{"./_descriptors":14,"./_dom-create":15,"./_fails":17}],22:[function(require,module,exports){
module.exports = function (it) {
  return typeof it === 'object' ? it !== null : typeof it === 'function';
};

},{}],23:[function(require,module,exports){
var anObject = require('./_an-object');
var IE8_DOM_DEFINE = require('./_ie8-dom-define');
var toPrimitive = require('./_to-primitive');
var dP = Object.defineProperty;

exports.f = require('./_descriptors') ? Object.defineProperty : function defineProperty(O, P, Attributes) {
  anObject(O);
  P = toPrimitive(P, true);
  anObject(Attributes);
  if (IE8_DOM_DEFINE) try {
    return dP(O, P, Attributes);
  } catch (e) { /* empty */ }
  if ('get' in Attributes || 'set' in Attributes) throw TypeError('Accessors not supported!');
  if ('value' in Attributes) O[P] = Attributes.value;
  return O;
};

},{"./_an-object":11,"./_descriptors":14,"./_ie8-dom-define":21,"./_to-primitive":25}],24:[function(require,module,exports){
module.exports = function (bitmap, value) {
  return {
    enumerable: !(bitmap & 1),
    configurable: !(bitmap & 2),
    writable: !(bitmap & 4),
    value: value
  };
};

},{}],25:[function(require,module,exports){
// 7.1.1 ToPrimitive(input [, PreferredType])
var isObject = require('./_is-object');
// instead of the ES6 spec version, we didn't implement @@toPrimitive case
// and the second argument - flag - preferred type is a string
module.exports = function (it, S) {
  if (!isObject(it)) return it;
  var fn, val;
  if (S && typeof (fn = it.toString) == 'function' && !isObject(val = fn.call(it))) return val;
  if (typeof (fn = it.valueOf) == 'function' && !isObject(val = fn.call(it))) return val;
  if (!S && typeof (fn = it.toString) == 'function' && !isObject(val = fn.call(it))) return val;
  throw TypeError("Can't convert object to primitive value");
};

},{"./_is-object":22}],26:[function(require,module,exports){
var $export = require('./_export');
// 19.1.2.4 / 15.2.3.6 Object.defineProperty(O, P, Attributes)
$export($export.S + $export.F * !require('./_descriptors'), 'Object', { defineProperty: require('./_object-dp').f });

},{"./_descriptors":14,"./_export":16,"./_object-dp":23}]},{},[2])
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCJhZ2VudC9ob29rLnRzIiwiYWdlbnQvaW5kZXgudHMiLCJhZ2VudC9zY2VuYXJpby50cyIsImxpYi9jb2xvci50cyIsIm5vZGVfbW9kdWxlcy9AYmFiZWwvcnVudGltZS1jb3JlanMyL2NvcmUtanMvanNvbi9zdHJpbmdpZnkuanMiLCJub2RlX21vZHVsZXMvQGJhYmVsL3J1bnRpbWUtY29yZWpzMi9jb3JlLWpzL29iamVjdC9kZWZpbmUtcHJvcGVydHkuanMiLCJub2RlX21vZHVsZXMvQGJhYmVsL3J1bnRpbWUtY29yZWpzMi9oZWxwZXJzL2ludGVyb3BSZXF1aXJlRGVmYXVsdC5qcyIsIm5vZGVfbW9kdWxlcy9jb3JlLWpzL2xpYnJhcnkvZm4vanNvbi9zdHJpbmdpZnkuanMiLCJub2RlX21vZHVsZXMvY29yZS1qcy9saWJyYXJ5L2ZuL29iamVjdC9kZWZpbmUtcHJvcGVydHkuanMiLCJub2RlX21vZHVsZXMvY29yZS1qcy9saWJyYXJ5L21vZHVsZXMvX2EtZnVuY3Rpb24uanMiLCJub2RlX21vZHVsZXMvY29yZS1qcy9saWJyYXJ5L21vZHVsZXMvX2FuLW9iamVjdC5qcyIsIm5vZGVfbW9kdWxlcy9jb3JlLWpzL2xpYnJhcnkvbW9kdWxlcy9fY29yZS5qcyIsIm5vZGVfbW9kdWxlcy9jb3JlLWpzL2xpYnJhcnkvbW9kdWxlcy9fY3R4LmpzIiwibm9kZV9tb2R1bGVzL2NvcmUtanMvbGlicmFyeS9tb2R1bGVzL19kZXNjcmlwdG9ycy5qcyIsIm5vZGVfbW9kdWxlcy9jb3JlLWpzL2xpYnJhcnkvbW9kdWxlcy9fZG9tLWNyZWF0ZS5qcyIsIm5vZGVfbW9kdWxlcy9jb3JlLWpzL2xpYnJhcnkvbW9kdWxlcy9fZXhwb3J0LmpzIiwibm9kZV9tb2R1bGVzL2NvcmUtanMvbGlicmFyeS9tb2R1bGVzL19mYWlscy5qcyIsIm5vZGVfbW9kdWxlcy9jb3JlLWpzL2xpYnJhcnkvbW9kdWxlcy9fZ2xvYmFsLmpzIiwibm9kZV9tb2R1bGVzL2NvcmUtanMvbGlicmFyeS9tb2R1bGVzL19oYXMuanMiLCJub2RlX21vZHVsZXMvY29yZS1qcy9saWJyYXJ5L21vZHVsZXMvX2hpZGUuanMiLCJub2RlX21vZHVsZXMvY29yZS1qcy9saWJyYXJ5L21vZHVsZXMvX2llOC1kb20tZGVmaW5lLmpzIiwibm9kZV9tb2R1bGVzL2NvcmUtanMvbGlicmFyeS9tb2R1bGVzL19pcy1vYmplY3QuanMiLCJub2RlX21vZHVsZXMvY29yZS1qcy9saWJyYXJ5L21vZHVsZXMvX29iamVjdC1kcC5qcyIsIm5vZGVfbW9kdWxlcy9jb3JlLWpzL2xpYnJhcnkvbW9kdWxlcy9fcHJvcGVydHktZGVzYy5qcyIsIm5vZGVfbW9kdWxlcy9jb3JlLWpzL2xpYnJhcnkvbW9kdWxlcy9fdG8tcHJpbWl0aXZlLmpzIiwibm9kZV9tb2R1bGVzL2NvcmUtanMvbGlicmFyeS9tb2R1bGVzL2VzNi5vYmplY3QuZGVmaW5lLXByb3BlcnR5LmpzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiJBQUFBOzs7Ozs7Ozs7Ozs7OztBQ0FBLElBQUEsT0FBQSxHQUFBLE9BQUEsQ0FBQSxjQUFBLENBQUE7O0FBR0EsSUFBaUIsT0FBakI7O0FBQUEsQ0FBQSxVQUFpQixPQUFqQixFQUF3QjtBQUVwQixXQUFnQixzQkFBaEIsQ0FBdUMsY0FBdkMsRUFBMEQ7QUFDdEQsUUFBSTtBQUNBLFVBQUksT0FBTyxjQUFQLElBQTBCLFFBQTlCLEVBQXdDO0FBQ3BDLFFBQUEsY0FBYyxHQUFHLElBQUksQ0FBQyxHQUFMLENBQVMsY0FBVCxDQUFqQjtBQUNIOztBQUNELFVBQUksWUFBWSxHQUFhLGNBQWMsU0FBZCxDQUFxQixrQkFBckIsR0FBMEMsTUFBMUMsQ0FBaUQsVUFBUyxNQUFULEVBQXFCO0FBQy9GLFlBQUksTUFBTSxDQUFDLE9BQVAsR0FBaUIsT0FBakIsQ0FBeUIsR0FBekIsS0FBaUMsQ0FBckMsRUFBd0M7QUFDcEMsaUJBQU8sS0FBUDtBQUNIOztBQUNELGVB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QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUM5REE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNQQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNOQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQ0pBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7QUNSQTtBQUNBO0FBQ0E7QUFDQTs7QUNIQTtBQUNBO0FBQ0E7QUFDQTs7QUNIQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOztBQ2hCQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FDUkE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7O0FDWkE7QUFDQTtBQUNBO0FBQ0EiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiJ9
