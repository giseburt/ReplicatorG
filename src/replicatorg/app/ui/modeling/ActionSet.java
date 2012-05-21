package replicatorg.app.ui.modeling;

import java.awt.Font;

import java.util.Vector;

import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingConstants;

import net.miginfocom.swing.MigLayout;

import replicatorg.app.ui.BGPanel;

public class ActionSet {
	final PreviewPanel preview;
	final BGPanel toolbarPanel;
	
	final JPanel subPanel = new JPanel(new MigLayout("fillx,filly,ins 0,gap 0"));
	Vector<Tool> tools;
	
	ActionSet(final PreviewPanel preview, final BGPanel toolbarPanel) {
		this.preview = preview;
		this.toolbarPanel = toolbarPanel;
	
		// Border border = UIManager.getBorder("TitledBorder.aquaVariant");
		// if (border == null) border = BorderFactory.createEtchedBorder();
		//subPanel.setBorder(BorderFactory.createTitledBorder(border, "Title"));
	}
}