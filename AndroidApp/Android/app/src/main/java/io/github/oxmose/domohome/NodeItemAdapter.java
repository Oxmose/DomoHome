package io.github.oxmose.domohome;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.switchmaterial.SwitchMaterial;

import java.util.List;

public class NodeItemAdapter extends RecyclerView.Adapter<NodeItemAdapter.ViewHolder> {
    private List<NodeItem> nodes;

    @NonNull
    @Override
    public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(parent.getContext());
        View nodeView = inflater.inflate(R.layout.item_node, parent, false);
        return new ViewHolder(nodeView);
    }

    @Override
    public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
        NodeItem node = nodes.get(position);

        TextView textView = holder.nodeName;
        textView.setText(node.getName());
        SwitchMaterial switchInfo = holder.isSelectedSwitch;
        switchInfo.setSelected(node.isSelected());

        textView.setClickable(true);
        textView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                node.toggleSelected();
                switchInfo.setSelected(node.isSelected());
            }
        });

        switchInfo.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                node.toggleSelected();
            }
        });
    }

    @Override
    public int getItemCount() {
        return nodes.size();
    }

    public class ViewHolder extends RecyclerView.ViewHolder {
        public TextView nodeName;
        public SwitchMaterial isSelectedSwitch;

        public ViewHolder(View itemView) {
            super(itemView);

            nodeName = itemView.findViewById(R.id.node_name_textview);
            isSelectedSwitch = itemView.findViewById(R.id.node_is_selected_switch);
        }
    }

    public NodeItemAdapter(List<NodeItem> nodes) {
        this.nodes = nodes;
    }
}
