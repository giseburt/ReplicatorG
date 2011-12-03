package replicatorg.app.ui;

import java.awt.Graphics;
import java.awt.Rectangle;
import java.awt.image.BufferedImage;
import java.awt.Color;
import replicatorg.app.Base;

import javax.swing.JPanel;

/**
 * BGPanel serves but one purpose: to get past the hideousness of the Mac L+F and actually draw
 * a freaking background.
 * 
 * @author phooky
 *
 */
public class BGPanel extends JPanel {
	BufferedImage backgroundImg = null;
	int vOffset = 0;
	
	public BGPanel() {
		setOpaque(true);
	}
	
	public void setBackground(BufferedImage bg, int offset) {
		backgroundImg = bg;
		vOffset = offset;
	}
	
	public void paintComponent(Graphics g1) {
		Graphics g = g1.create();
		g.setPaintMode();
		super.paintComponent(g);
		Rectangle r = getBounds();
		if (backgroundImg != null) {
			int height = backgroundImg.getHeight();
			int width = backgroundImg.getWidth();
			
			g.drawImage(backgroundImg, 0 , vOffset, r.width, height+vOffset, 0, 0, 1, height, null);
		} else if (getBackground() != null) {
			g.setColor(getBackground());
			g.fillRect(r.x,r.y,r.width,r.height);
		}
	}
	// 
	// 
	// public void paint(Graphics g) {
	// 	g.setColor(getBackground());
	// 	paintComponent(g);
	// 	paintChildren(g);
	// }
}
