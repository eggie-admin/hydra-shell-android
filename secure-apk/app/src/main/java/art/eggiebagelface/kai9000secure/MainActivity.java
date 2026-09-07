package art.eggiebagelface.kai9000secure;

import android.Manifest;
import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.os.*;
import android.widget.*;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

public final class MainActivity extends Activity {
    private TextView status;

    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        buildUi();

        if (Build.VERSION.SDK_INT >= 33 &&
            checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 9000);
        }
    }

    @Override protected void onStart() {
        super.onStart();
        startBackend();
        refreshStatus();
    }

    private void buildUi() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(48, 64, 48, 48);

        TextView title = new TextView(this);
        title.setText("KAI 9000 SECURE");
        title.setTextSize(28);
        title.setTypeface(Typeface.DEFAULT_BOLD);
        box.addView(title);

        TextView doctrine = new TextView(this);
        doctrine.setText("\nOne APK • localhost only • no Termux • no AcodeX\nSecure Folder owns the app data.\n");
        doctrine.setTextSize(16);
        box.addView(doctrine);

        status = new TextView(this);
        status.setText("Checking 127.0.0.1:8000...");
        status.setTextSize(16);
        status.setTextIsSelectable(true);
        box.addView(status);

        Button start = new Button(this);
        start.setText("START BACKEND");
        start.setOnClickListener(v -> { startBackend(); refreshStatus(); });
        box.addView(start);

        Button stop = new Button(this);
        stop.setText("STOP BACKEND");
        stop.setOnClickListener(v -> {
            Intent i = new Intent(this, KaiBackendService.class).setAction(KaiBackendService.ACTION_STOP);
            startService(i);
            status.setText("STOP requested.");
        });
        box.addView(stop);

        Button refresh = new Button(this);
        refresh.setText("HEALTH CHECK");
        refresh.setOnClickListener(v -> refreshStatus());
        box.addView(refresh);

        setContentView(box);
    }

    private void startBackend() {
        Intent i = new Intent(this, KaiBackendService.class).setAction(KaiBackendService.ACTION_START);
        if (Build.VERSION.SDK_INT >= 26) startForegroundService(i);
        else startService(i);
    }

    private void refreshStatus() {
        status.setText("Checking...");
        Executors.newSingleThreadExecutor().execute(() -> {
            String result;
            try {
                HttpURLConnection c = (HttpURLConnection) new URL("http://127.0.0.1:8000/api/health").openConnection();
                c.setConnectTimeout(1500);
                c.setReadTimeout(1500);
                c.setUseCaches(false);
                int code = c.getResponseCode();
                try (InputStream in = code >= 400 ? c.getErrorStream() : c.getInputStream()) {
                    result = code + " " + new String(in.readAllBytes(), StandardCharsets.UTF_8);
                }
                c.disconnect();
            } catch (Exception e) {
                result = "OFFLINE: " + e.getClass().getSimpleName() + ": " + e.getMessage();
            }
            String finalResult = result;
            runOnUiThread(() -> status.setText(finalResult));
        });
    }
}
