package art.eggiebagelface.kai9000secure;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public final class KaiDb extends SQLiteOpenHelper {
    private static final String DB_NAME = "kai9000.sqlite3";
    private static final int DB_VERSION = 1;

    public KaiDb(Context context) {
        super(context, DB_NAME, null, DB_VERSION);
    }

    @Override public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE kv (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at INTEGER NOT NULL)");
        db.execSQL("CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, payload TEXT NOT NULL, created_at INTEGER NOT NULL)");
    }

    @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
    }

    public synchronized void put(String key, String value) {
        SQLiteDatabase db = getWritableDatabase();
        db.execSQL(
            "INSERT INTO kv(key,value,updated_at) VALUES(?,?,?) " +
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
            new Object[]{key, value, System.currentTimeMillis() / 1000L}
        );
    }

    public synchronized String get(String key) {
        SQLiteDatabase db = getReadableDatabase();
        try (Cursor c = db.rawQuery("SELECT value FROM kv WHERE key=?", new String[]{key})) {
            return c.moveToFirst() ? c.getString(0) : null;
        }
    }

    public synchronized void event(String kind, String payload) {
        getWritableDatabase().execSQL(
            "INSERT INTO events(kind,payload,created_at) VALUES(?,?,?)",
            new Object[]{kind, payload, System.currentTimeMillis() / 1000L}
        );
    }
}
