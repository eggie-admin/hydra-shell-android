package art.eggiebagelface.kai9000secure;

import android.app.*;
import android.content.*;
import android.content.pm.ServiceInfo;
import android.os.*;

public final class KaiBackendService extends Service {
    public static final String ACTION_START = "art.eggiebagelface.kai9000secure.START";
    public static final String ACTION_STOP = "art.eggiebagelface.kai9000secure.STOP";
    private static final String CHANNEL_ID = "kai9000_backend";
    private static final int NOTIFICATION_ID = 9000;
    private LocalHttpServer server;

    @Override public void onCreate() {
        super.onCreate();
        createChannel();
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            stopBackend();
            stopForeground(STOP_FOREGROUND_REMOVE);
            stopSelf();
            return START_NOT_STICKY;
        }

        startAsForeground();
        if (server == null) {
            server = new LocalHttpServer(this);
            try {
                server.start();
            } catch (Exception e) {
                stopForeground(STOP_FOREGROUND_REMOVE);
                stopSelf();
            }
        }
        return START_STICKY;
    }

    private void startAsForeground() {
        Intent open = new Intent(this, MainActivity.class);
        PendingIntent openPi = PendingIntent.getActivity(
            this, 1, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Intent stop = new Intent(this, KaiBackendService.class).setAction(ACTION_STOP);
        PendingIntent stopPi = PendingIntent.getService(
            this, 2, stop, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        Notification notification = new Notification.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.stat_sys_upload_done)
            .setContentTitle("KAI 9000 backend")
            .setContentText("127.0.0.1:8000 • Secure Folder localhost")
            .setOngoing(true)
            .setContentIntent(openPi)
            .addAction(new Notification.Action.Builder(null, "Stop", stopPi).build())
            .build();

        if (Build.VERSION.SDK_INT >= 34) {
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE);
        } else {
            startForeground(NOTIFICATION_ID, notification);
        }
    }

    private void createChannel() {
        NotificationManager nm = getSystemService(NotificationManager.class);
        NotificationChannel ch = new NotificationChannel(
            CHANNEL_ID, "KAI 9000 backend", NotificationManager.IMPORTANCE_LOW);
        ch.setDescription("Persistent localhost control-plane status");
        nm.createNotificationChannel(ch);
    }

    private void stopBackend() {
        if (server != null) {
            server.stop();
            server = null;
        }
    }

    @Override public void onDestroy() {
        stopBackend();
        super.onDestroy();
    }

    @Override public android.os.IBinder onBind(Intent intent) {
        return null;
    }
}
