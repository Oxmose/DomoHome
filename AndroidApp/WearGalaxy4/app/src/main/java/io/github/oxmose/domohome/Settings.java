package io.github.oxmose.domohome;

import android.content.Context;
import android.content.SharedPreferences;

public class Settings {

    /* Sharedpreferences reader and editor */
    private SharedPreferences        reader;
    private SharedPreferences.Editor writer;

    private static Settings instance = null;

    public static Settings getInstance(Context context) {
        if(instance == null) {
            instance = new Settings(context);
        }
        return instance;
    }

    private Settings(Context context) {
        /* Get shared preference reader and writer */
        reader = context.getSharedPreferences("io.github.oxmose.domohome", Context.MODE_PRIVATE);
        writer = reader.edit();
    }

    public String getServerIP() {
        return reader.getString("serverIP", "");
    }

    public String getServerAPIKey() {
        return reader.getString("serverAPIKey", "");
    }

    public void setServerIP(String serverIP) {
        writer.putString("serverIP", serverIP).commit();
    }

    public void setServerAPIKey(String serverAPIKey) {
        writer.putString("serverAPIKey", serverAPIKey).commit();
    }
}