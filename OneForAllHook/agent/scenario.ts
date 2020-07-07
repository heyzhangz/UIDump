import { hooking as h } from './hook';


export function cameraReleatedHook(trace_flag: boolean, arg_vals: boolean) {
    let target_classes:string[];
    target_classes = [
      'android.hardware.Camera', 
      'android.hardware.camera2.CameraManager', 
      'android.hardware.camera2.CaptureResult', 
      'android.hardware.camera2.CaptureRequest',
      'android.hardware.camera2.impl.CameraDeviceImpl'
    ]
    target_classes.forEach((clazz) => {
      h.hook_class_methods(clazz, trace_flag, arg_vals);
    });
}

export function locationReleatedHook(trace_flag: boolean, arg_vals: boolean) {
    let target_classes:string[];
    target_classes = [
      "android.location.GpsStatus$SatelliteIterator",
      "android.location.IGnssStatusListener$Stub",
      "android.location.GpsStatus$SatelliteIterator",
      "android.location.LocationManager$GnssStatusListenerTransport$GnssHandler",
      "android.location.LocationManager$GnssStatusListenerTransport",
      "android.location.GpsSatellite",
      "android.location.LocationManager",
      "android.location.GpsStatus",
      "android.location.GpsStatus$1",
      "android.location.Location"
    ]
    target_classes.forEach((clazz) => {
      h.hook_class_methods(clazz, trace_flag, arg_vals);
    })
}

export function audioReleatedHook(trace_flag: boolean, arg_vals: boolean) {
    let target_classes:string[];
    target_classes = [
      'android.media.MediaPlayer',
      'android.media.MediaPlayer$TimeProvider',
      'android.media.AudioTrack',
      'android.media.PlayerBase',
      'android.speech.tts.TextToSpeech',
      'android.media.SoundPool'
    ]
    target_classes.forEach((clazz) => {
      h.hook_class_methods(clazz, trace_flag, arg_vals);
    })
}

export function mircophoneReleatedHook(trace_flag: boolean, arg_vals: boolean) {
    let target_classes:string[];
    target_classes = [
        'android.media.AudioRecord',
        'android.media.AudioManager',
        'android.media.MediaRecorder'
    ]
    target_classes.forEach((clazz) => {
      h.hook_class_methods(clazz, trace_flag, arg_vals);
    })
}

export function contactReleatedHook(trace_flag: boolean, arg_vals: boolean) {
    let target_classes:string[];
    target_classes = [
        'android.provider.ContactsContract',
        'android.provider.ContactsContract$RawContacts',
        'android.content.ContentResolver',
        // contact 和 sms 区分可能需要解析Uri
        // 'android.net.Uri$StringUri',
        // 'android.net.Uri'
    ]
    target_classes.forEach((clazz) => {
      h.hook_class_methods(clazz, trace_flag, arg_vals);
    })

    // android.net.Uri 调用地点比较多，主要hook parse方法
    h.hook_target_method('android.net.Uri', 'parse', '', '', trace_flag, arg_vals)
}

export function smsReleatedHook(trace_flag: boolean, arg_vals: boolean) {
    let target_classes:string[];
    // android.provider.Telephony.Sms见的比较少，大多数直接查询
    // 读取短信也是查询数据库和contact类似，但是sms数据库中有date信息，通常读取时会格式化时间戳，调用太频繁了
    target_classes = [
        // 'android.icu.text.SimpleDateFormat',
        // 'java.text.SimpleDateFormat',
        'android.provider.Telephony$Sms',
        'android.provider.Telephony$Mms',
        'android.provider.Telephony',
        'android.telephony.TelephonyManager'
    ]
    target_classes.forEach((clazz) => {
      h.hook_class_methods(clazz, trace_flag, arg_vals);
    })
}

export function life_cycle_hook(trace_flag: boolean, arg_vals: boolean) {
  let target_classes:string[];
  target_classes = [
    'android.app.Activity',
    'android.app.Service'
  ]
  target_classes.forEach((clazz) => {
    h.hook_target_method(clazz, 'onCreate', '', '', trace_flag, arg_vals);
  })
}

export function permission_request_hook(trace_flag: boolean, arg_vals: boolean) {
  h.hook_target_method('android.app.Activity', 'requestPermissions', '', '', trace_flag, arg_vals);
  h.hook_target_method('android.app.Fragment', 'requestPermissions', '', '', trace_flag, arg_vals);
}

export function ad_hook() {
    let google_target_classes = [
        'com.google.android.gms.ads.AdRequest$Builder',
        'com.google.android.gms.ads.doubleclick.PublisherAdRequest$Builder',
        'com.google.android.gms.ads.search.SearchAdRequest$Builder',
        // 特殊混淆情况
        'com.google.android.gms.ads.c$a',
        'com.google.android.gms.ads.d$a',
    ]
    google_target_classes.forEach((google_target_class) => {
        h.get_class_method_names(google_target_class).forEach((method) => {
            h.hook_target_method(google_target_class, method, 'android.location.Location', '', true, false)
            if (method == 'setGender' || method == 'setBirthday') {
                h.hook_target_method(google_target_class, method, '', '', true, false)
            }
        })
    })

    // facebook 没找到地理位置接口
    // let fb_target_class = ''

    let mopub_target_class = 'com.mopub.common.AdUrlGenerator'
    h.get_class_method_names(mopub_target_class).forEach((method) => {
        h.hook_target_method(mopub_target_class, method, 'android.location.Location', 'void', true, false)
    })

    //旧版本Mopub没有带参数的setLocation方法，可以用旧版本的getLastKnownLocation判断，和新版本的不同
    let mopub_target_class_old = 'com.mopub.common.LocationService'
    h.get_class_method_names(mopub_target_class_old).forEach((method) => {
        h.hook_target_method(mopub_target_class_old, method, 'android.content.Context',
            'android.location.Location', true, false)
    })


    let amazon_target_classes = [
        'com.amazon.device.ads.AdLocation',
        'com.amazon.device.ads.DtbGeoLocation',
    ]
    amazon_target_classes.forEach((amazon_target_class) => {
        h.get_class_method_names(amazon_target_class).forEach((method) => {
            h.hook_target_method(amazon_target_class, method, 'void', 'android.location.Location', true, false)
        })
    })

    // flurry本身sdk就已经混淆了
    let flurry_target_class = 'com.flurry.sdk.ads.cf'
    h.get_class_method_names(flurry_target_class).forEach((method) => {
        h.hook_target_method(flurry_target_class, method, '', 'android.location.Location', true, false)
    })

    let inmobi_target_class = 'com.inmobi.sdk.InMobiSdk'
    h.get_class_method_names(inmobi_target_class).forEach((method) => {
        h.hook_target_method(inmobi_target_class, method, 'android.location.Location', '', true, false)
        //setLocationWithCityStateCountry
        h.hook_target_method(inmobi_target_class, method, 'java.lang.String,java.lang.String,java.lang.String', '', true, false)
    })

    let adcolony_target_class = 'com.adcolony.sdk.AdColonyUserMetadata'
    h.get_class_method_names(adcolony_target_class).forEach((method) => {
        h.hook_target_method(adcolony_target_class, method, 'android.location.Location', '', true, false)
        if (method == 'setUserGender' || method == 'setUserAge') {
                h.hook_target_method(adcolony_target_class, method, '', '', true, false)
            }
    })

    // appLovin sdk类名混淆，并且本身用的好像是WebSettings的setGeolocationEnabled
    // let appLovin_target_class = ''

    // appodeal sdk类名混淆，并且用的比较少 都是bm
    let appodeal_target_class = 'com.appodeal.ads.bm'
    h.get_class_method_names(appodeal_target_class).forEach((method) => {
        h.hook_target_method(appodeal_target_class, method, '', 'android.location.Location', true, false)
    })
}

export function test_func() {
    h.hook_target_method('android.location.Location', 'distanceBetween', '', '', true, true);
}
