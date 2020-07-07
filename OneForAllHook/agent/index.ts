import {cameraReleatedHook, locationReleatedHook, audioReleatedHook, life_cycle_hook, permission_request_hook, ad_hook, test_func, mircophoneReleatedHook, contactReleatedHook, smsReleatedHook} from './scenario'

Java.performNow(function() {
    if(Java.available) {
        console.log('[+] JVM load success');
        locationReleatedHook(true, false);
        cameraReleatedHook(true, true);
        audioReleatedHook(true, true);
        mircophoneReleatedHook(true, true);
        contactReleatedHook(true, true);
        smsReleatedHook(true, true);
        life_cycle_hook(false, false);
        permission_request_hook(true, false);
        // test_func();
    }
});

Java.perform(function() {
    if(Java.available) {
        console.log('[+] JVM load success');
        ad_hook();
    }
});
