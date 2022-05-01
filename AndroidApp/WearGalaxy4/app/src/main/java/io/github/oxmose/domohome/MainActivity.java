package io.github.oxmose.domohome;

import android.app.Activity;
import android.content.Intent;
import android.content.res.Resources;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.akexorcist.roundcornerprogressbar.TextRoundCornerProgressBar;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.Callable;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

import io.github.oxmose.domohome.databinding.ActivityMainBinding;
import me.bastanfar.semicirclearcprogressbar.SemiCircleArcProgressBar;

public class MainActivity extends Activity {

    private static final double FACTOR = 0.02f;
    private static final double MIN_TEMP_ENV = 10.0f;
    private static final double MAX_TEMP_ENV = 30.0f;
    private static final String REST_API_GET_ENV = "/getEnvlast";
    private static final String REST_API_GET_NAS = "/getNASStatus";

    private String serverIP;
    private String serverAPIKey;

    private TextView temperatureTextView;
    private TextView humidityTextView;
    private TextView lightTextView;

    private SemiCircleArcProgressBar tempProgressBar;
    private SemiCircleArcProgressBar humProgressBar;
    private SemiCircleArcProgressBar lumProgressBar;

    private ImageView ftpStatusImageView;
    private ImageView smbStatusImageView;

    private TextView nasIPTextView;
    private TextView nasUsageTextView;

    private TextRoundCornerProgressBar nasUsageBar;

    private SwipeRefreshLayout swipeToRefresh;

    private ActivityMainBinding binding;

    private ImageButton settingsButton;

    private Lock refreshLock;
    private int  refreshCount;

    public interface Callback<R> {
        void onComplete(R result);
    }

    class AsynchDataGetter {
        private final Executor executor = Executors.newSingleThreadExecutor();
        private final Handler handler = new Handler(Looper.getMainLooper());

        public <R> void executeAsync(Callable<R> callable, Callback<R> callback) {
            executor.execute(() -> {
                final R result;
                try {
                    result = callable.call();
                    handler.post(() -> {
                        callback.onComplete(result);
                    });
                }
                catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }
    }

    protected JSONObject getRESTJson(String JSON_URL) {
        JSONObject retObj = null;
        boolean updated = false;
        HttpURLConnection conn;
        StringBuilder result;
        URL urlObj;

        refreshLock.lock();
        ++refreshCount;
        swipeToRefresh.setRefreshing(true);
        refreshLock.unlock();

        do {
            try {
                urlObj = new URL(JSON_URL);

                conn = (HttpURLConnection) urlObj.openConnection();
                conn.setDoOutput(false);
                conn.setRequestMethod("GET");
                conn.setRequestProperty("Content-Type", "application/json; utf-8");
                conn.setRequestProperty("Accept", "application/json");
                conn.setConnectTimeout(3000);
                conn.connect();

                InputStream in = new BufferedInputStream(conn.getInputStream());
                BufferedReader reader = new BufferedReader(new InputStreamReader(in));
                result = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    result.append(line);
                }

                conn.disconnect();
                reader.close();
                in.close();

                retObj = new JSONObject(result.toString());
                updated = true;
            }
            catch (IOException | JSONException e) {
                e.printStackTrace();
            }
        }while(!updated); /* TODO: Add a timeout */

        return retObj;
    }

    protected void updateEnvUI(JSONObject json) {
        int percent;

        if (json != null) {
            JSONObject envData = null;
            try {
                envData = json.getJSONObject("lastEnv");
                temperatureTextView.setText(getString(R.string.temp_formated_text, envData.getString("t")));
                humidityTextView.setText(getString(R.string.hum_formated_text, envData.getString("h")));
                lightTextView.setText(getString(R.string.light_formated_text, envData.getString("l")));

                percent = (int)((Double.parseDouble(envData.getString("t")) - MIN_TEMP_ENV) * 100.0 / MAX_TEMP_ENV);

                tempProgressBar.setPercent(percent);
                humProgressBar.setPercent((int)Double.parseDouble(envData.getString("h")));
                lumProgressBar.setPercent((int)Double.parseDouble(envData.getString("l")));


                refreshLock.lock();
                --refreshCount;
                if(refreshCount == 0) {
                    swipeToRefresh.setRefreshing(false);
                }
                refreshLock.unlock();
            }
            catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    protected void updateNASStatusUI(JSONObject json) {
        if (json != null) {
            try {
                if(json.getBoolean("ftpEnabled")) {
                    ftpStatusImageView.setImageDrawable(getDrawable(R.drawable.ic_baseline_check_circle_outline_24));
                    ftpStatusImageView.setColorFilter(Color.parseColor("#4DB6AC"));
                }
                else {
                    ftpStatusImageView.setImageDrawable(getDrawable(R.drawable.ic_outline_cancel_24));
                    ftpStatusImageView.setColorFilter(Color.parseColor("#E57373"));
                }

                if(json.getBoolean("smbdEnabled")) {
                    smbStatusImageView.setImageDrawable(getDrawable(R.drawable.ic_baseline_check_circle_outline_24));
                    smbStatusImageView.setColorFilter(Color.parseColor("#4DB6AC"));
                }
                else {
                    smbStatusImageView.setImageDrawable(getDrawable(R.drawable.ic_outline_cancel_24));
                    smbStatusImageView.setColorFilter(Color.parseColor("#E57373"));
                }

                nasIPTextView.setText(getString(R.string.ip_address_formated, "192.168.1.203"));
                nasUsageTextView.setText(getString(R.string.nas_usage_formated, json.getString("diskUsed"),
                        json.getString("diskUsedUnit"),
                        json.getString("diskTotal"),
                        json.getString("diskTotalUnit")));

                nasUsageBar.setProgress((int)Double.parseDouble(json.getString("diskPercent")));
                //nasUsageBar.setProgressText(String.format("%.1f%%", Double.parseDouble(json.getString("diskPercent"))));

                refreshLock.lock();
                --refreshCount;
                if(refreshCount == 0) {
                    swipeToRefresh.setRefreshing(false);
                }
                refreshLock.unlock();
            }
            catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }

    private void getInterfaceElements() {
        temperatureTextView = binding.textViewTemperature;
        humidityTextView    = binding.textViewHumidity;
        lightTextView       = binding.textViewLight;

        tempProgressBar = binding.progressBarTemperature;
        humProgressBar  = binding.progressBarHumidity;
        lumProgressBar  = binding.progressBarLuminosity;

        ftpStatusImageView = binding.imageViewFtpEnabled;
        smbStatusImageView = binding.imageViewSmbEnabled;

        nasIPTextView     = binding.textViewNastatusIpAddressText;
        nasUsageTextView  = binding.textViewNastatusUsageText;

        nasUsageBar = binding.progressBarNasStatusBar;

        swipeToRefresh = binding.swiperefresh;

        settingsButton = binding.settingsButton;
    }

    protected void updateUI() {
        Settings settings = Settings.getInstance(null);

        /* Update environment data */
        new AsynchDataGetter().executeAsync(
                () -> getRESTJson(settings.getServerIP() + REST_API_GET_ENV + "/" + settings.getServerAPIKey()),
                result -> updateEnvUI(result));

        /* Update NAS status */
        new AsynchDataGetter().executeAsync(
                () -> getRESTJson(settings.getServerIP() + REST_API_GET_NAS + "/" + settings.getServerAPIKey()),
                result -> updateNASStatusUI(result));
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Settings settings = Settings.getInstance(getApplicationContext());

        /* Load settings */
        serverIP     = settings.getServerIP();
        serverAPIKey = settings.getServerAPIKey();

        /* If no settings are given, go to settings page */
        if(serverIP.length() == 0 || serverAPIKey.length() == 0) {
            Intent settingActivity = new Intent(this, SettingsActivity.class);
            startActivity(settingActivity);
            finish();
            return;
        }

        /* Initialize UI */
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());
        getInterfaceElements();

        if(getApplicationContext().getResources().getConfiguration().isScreenRound()) {
            int inset = (int) (FACTOR * Resources.getSystem().getDisplayMetrics().widthPixels);
            binding.frameLayout.setPadding(inset, inset, inset, inset);
        }

        /* Initialize data */
        refreshLock  = new ReentrantLock();
        refreshCount = 0;

        /* Update UI */
        updateUI();

        swipeToRefresh.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                updateUI();
            }
        });

        settingsButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent settingActivity = new Intent(MainActivity.this, SettingsActivity.class);
                startActivity(settingActivity);
            }
        });
    }
}