package io.github.oxmose.domohome;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.util.Log;

import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.google.android.gms.wearable.DataClient;
import com.google.android.gms.wearable.MessageEvent;
import com.google.android.gms.wearable.Wearable;
import com.google.android.gms.wearable.WearableListenerService;

public class SettingsActivity extends Activity {

    public class Receiver extends BroadcastReceiver {
        @Override
        public void onReceive(Context context, Intent intent) {
            String settings = intent.getExtras().getString("settingData");
            String[] settingsSplit = settings.split(";");

            Settings settingsSave = Settings.getInstance(getApplicationContext());
            settingsSave.setServerIP(settingsSplit[0]);
            settingsSave.setServerAPIKey(settingsSplit[1]);

            switchToMainActivity();
        }
    }

    private void switchToMainActivity() {
        Intent mainActivity = new Intent(this, MainActivity.class);
        startActivity(mainActivity);
        finish();
    }

    private void initDataClient() {
        IntentFilter newFilter   = new IntentFilter(Intent.ACTION_SEND);
        Receiver messageReceiver = new Receiver();

        LocalBroadcastManager.getInstance(this).registerReceiver(messageReceiver, newFilter);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings_page);

        /* Init the Data Client */
        initDataClient();
    }
}