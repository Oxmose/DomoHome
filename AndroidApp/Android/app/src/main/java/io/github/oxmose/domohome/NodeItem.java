package io.github.oxmose.domohome;

public class NodeItem {
    private String name;
    private boolean isSelected;

    public NodeItem(String name, boolean isSelected) {
        this.name = name;
        this.isSelected = isSelected;
    }

    public String getName() {
        return name;
    }

    public boolean isSelected() {
        return isSelected;
    }

    public void toggleSelected() {
        isSelected = !isSelected;
    }
}
