package art.eggiebagelface.kai9000secure;

import android.content.*;
import android.os.Build;

public final class BootReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context, Intent intent) {
        String action = intent == null ? null : intent.getAction();
        if (Intent.ACTION_BOOT_COMPLETED.equals(action) || Intent.ACTION_MY_PACKAGE_REPLACED.equals(action)) {
            Intent service = new Intent(context, KaiBackendService.class).setAction(KaiBackendService.ACTION_START);
            try {
                if (Build.VERSION.SDK_INT >= 26) context.startForegroundService(service);
                else context.startService(service);
            } catch (RuntimeException ignored) {
            }
        }
    }
}
