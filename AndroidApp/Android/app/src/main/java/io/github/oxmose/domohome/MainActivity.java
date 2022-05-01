package io.github.oxmose.domohome;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

import com.google.android.gms.nearby.messages.Message;
import com.google.android.gms.tasks.Task;
import com.google.android.gms.tasks.Tasks;
import com.google.android.gms.wearable.Node;
import com.google.android.gms.wearable.Wearable;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;

public class MainActivity extends AppCompatActivity {

    private EditText serverIPEditText;
    private EditText serverAPIKeyEditText;

    private Button sendButton;

    private SwipeRefreshLayout nodeListSwiper;
    private RecyclerView nodeListView;

    private List<NodeItem> nodeList;

    class SendDataThread extends Thread {

        private static final String SETTING_PATH = "/domohome/settings";

        private final String message;

        public SendDataThread(String serverIP, String serverAPIKey) {
            this.message = serverIP + ";" + serverAPIKey;
        }

        public void run() {
            Task<List<Node>> wearableList = Wearable.getNodeClient(getApplicationContext()).getConnectedNodes();
            try {

                List<Node> nodes = Tasks.await(wearableList);
                for (Node node : nodes) {
                    for (NodeItem nodeItem : nodeList) {
                        if(nodeItem.isSelected() && nodeItem.getName().equals(node.getDisplayName())) {
                            Task<Integer> sendMessageTask = Wearable.getMessageClient(MainActivity.this).sendMessage(node.getId(), SETTING_PATH, message.getBytes());
                            Integer result = Tasks.await(sendMessageTask);
                            Log.d("Send msg results", result.toString());
                        }
                    }
                }
            }
            catch (ExecutionException | InterruptedException exception) {
                Log.e("Error", exception.toString());
                exception.printStackTrace();
            }
        }
    }

    class RefreshNodesThread extends Thread {

        public RefreshNodesThread() {
        }

        public void run() {
            List<Node> nodes;
            Task<List<Node>> wearableList;

            nodeList = new ArrayList<>();
            wearableList = Wearable.getNodeClient(getApplicationContext()).getConnectedNodes();
            try {

                nodes = Tasks.await(wearableList);
                for (Node node : nodes) {
                    nodeList.add(new NodeItem(node.getDisplayName(), false));
                }
                nodeListView.setAdapter(new NodeItemAdapter(nodeList));
                nodeListView.setLayoutManager(new LinearLayoutManager(MainActivity.this));
                nodeListSwiper.setRefreshing(false);
            }
            catch (ExecutionException | InterruptedException exception) {
                Log.e("Error", exception.toString());
                exception.printStackTrace();
            }
        }
    }

    private void refreshConnectedNodes() {
        new RefreshNodesThread().start();
    }

    private void setupInterfaceElements() {
        serverIPEditText     = findViewById(R.id.serverip_edittext);
        serverAPIKeyEditText = findViewById(R.id.serverapikey_edittext);
        sendButton           = findViewById(R.id.senddata_button);

        nodeListSwiper = findViewById(R.id.node_list_swipelayout);
        nodeListView = findViewById(R.id.node_list_recyclerview);

        refreshConnectedNodes();

        sendButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                SendDataThread thread = new SendDataThread(serverIPEditText.getText().toString(),
                                                           serverAPIKeyEditText.getText().toString());
                thread.start();
            }
        });

        nodeListSwiper.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                refreshConnectedNodes();
            }
        });
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        /* Setup interface */
        setContentView(R.layout.activity_main);
        setupInterfaceElements();
    }
}