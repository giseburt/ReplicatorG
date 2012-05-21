/*
 Part of the ReplicatorG project - http://www.replicat.org
 Copyright (c) 2008 Zach Smith

 Forked from Arduino: http://www.arduino.cc

 Based on Processing http://www.processing.org
 Copyright (c) 2004-05 Ben Fry and Casey Reas
 Copyright (c) 2001-04 Massachusetts Institute of Technology

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software Foundation,
 Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

package replicatorg.app.ui;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.image.BufferedImage;
import java.awt.image.RescaleOp;
import java.awt.geom.Arc2D;
import java.awt.RenderingHints;
import java.lang.ref.WeakReference;
import java.util.Enumeration;

import javax.swing.AbstractButton;
import javax.swing.ButtonGroup;
import javax.swing.JComponent;
import javax.swing.JLabel;
import javax.swing.JToggleButton;
import javax.swing.border.EmptyBorder;
import javax.swing.event.ChangeEvent;
import javax.swing.event.ChangeListener;
import javax.swing.plaf.basic.BasicButtonUI;
import javax.swing.JPanel;
import javax.swing.JButton;
import javax.swing.SwingConstants;

import net.miginfocom.swing.MigLayout;
import replicatorg.app.Base;
import replicatorg.model.Build;
import replicatorg.model.BuildElement;

/**
 * Sketch tabs at the top of the editor window.
 */
public class EditorHeader extends JPanel implements ActionListener {
	private ButtonGroup tabGroup = new ButtonGroup();

	public interface BuildElementButton {
		public BuildElement getBuildElement();
		boolean isSelected();
	}

	public BuildElement getSelectedElement() {
		// Enumeration isn't iterable yet?
		Enumeration<AbstractButton> e = tabGroup.getElements();
		while (e.hasMoreElements()) {
			BuildElementButton beb = (BuildElementButton)e.nextElement();
			if (beb.isSelected()) { return beb.getBuildElement(); }
		}
		return null;
	}
	
	static Color backgroundColor;

	static Color textSelectedColor;
	static Color textUnselectedColor;
 
	private ChangeListener changeListener;
	void setChangeListener(ChangeListener listener) {
		changeListener = listener;
	}

	static BufferedImage selectedTabBg;
	static BufferedImage regularTabBg;

	static BufferedImage modelButtonIcon;
	static BufferedImage modelButtonSelectedIcon;
	static BufferedImage modelButtonOverIcon;
	static BufferedImage gcodeButtonIcon;
	static BufferedImage gcodeButtonSelectedIcon;
	static BufferedImage gcodeButtonOverIcon;
	
	protected void initTabImages() {
		if (selectedTabBg == null) {
			selectedTabBg = Base.getImage("images/tab-selected.png", this);
		}
		if (regularTabBg == null) {
			regularTabBg = Base.getImage("images/tab-regular.png", this);
		}
		if (modelButtonIcon == null) {
			modelButtonIcon = Base.getImage("images/model-view.png", this);
		}
		if (modelButtonSelectedIcon == null) {
			modelButtonSelectedIcon = Base.getImage("images/model-view-selected.png", this);
		}
		if (modelButtonOverIcon == null) {
			modelButtonOverIcon = Base.getImage("images/model-view-over.png", this);
		}
		if (gcodeButtonIcon == null) {
			gcodeButtonIcon = Base.getImage("images/gcode-view.png", this);
		}
		if (gcodeButtonSelectedIcon == null) {
			gcodeButtonSelectedIcon = Base.getImage("images/gcode-view-selected.png", this);
		}
		if (gcodeButtonOverIcon == null) {
			gcodeButtonOverIcon = Base.getImage("images/gcode-view-over.png", this);
		}
	}


	private class TabButton extends JToggleButton implements BuildElement.Listener,BuildElementButton {
		// Using a weak reference to work around massive leaks
		// http://bugs.sun.com/bugdatabase/view_bug.do?bug_id=4726458
		// This bug is almost old enough to attend high school.
		final WeakReference<Build> build;
		private ButtonGroup elementGroup = new ButtonGroup();
		
		// Whoa, we're getting deep! Sadly, very similar to TabButton... -RobG
		private class ElementButton extends JToggleButton implements BuildElement.Listener,BuildElementButton {
			final WeakReference<BuildElement> element;
			
			boolean isModel;
			
			float[] scales = { 1f, 1f, 1f, 0.5f };
			float[] offsets = new float[4];
			RescaleOp rop = new RescaleOp(scales, offsets, null);;
			
			public BuildElement getBuildElement() {
				return element.get();
			}

			public ElementButton(BuildElement element) {
				this.element = new WeakReference<BuildElement>(element);
				setBorder(new EmptyBorder(0,0,0,0));
				elementGroup.add(this);
				addActionListener(EditorHeader.this);
				setOpaque(false);
				element.addListener(this);
				setMinimumSize(new Dimension(22, 22));
				setRolloverEnabled(true);
				isModel = !(element.getType() == BuildElement.Type.GCODE);
			}
			
			public ElementButton(boolean isModel) {
				this.isModel = isModel;
				this.element = new WeakReference<BuildElement>(null);
				setBorder(new EmptyBorder(0,0,0,0));
				setOpaque(false);
				setMinimumSize(new Dimension(22, 22));
				setEnabled(false);
			}

			protected void paintComponent(Graphics g) {
				Graphics2D g2d = (Graphics2D)g;
				// draw the approprate circle...
				BufferedImage img = null;
				if (element.get() == null) {
				    g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

					g2d.drawImage(img, 0, 0, null);

				    Arc2D.Float arc = new Arc2D.Float(Arc2D.PIE);
				    arc.setFrame(1, 1, 20, 20);
				    arc.setAngleStart(90);
				    arc.setAngleExtent(-270);
				    g2d.setColor(new Color(1.0f,0.2f,0.2f,0.8f));
				    g2d.fill(arc);

					img = isModel?modelButtonIcon:gcodeButtonSelectedIcon;
					g2d.drawImage(img, rop,  0, 0);

					super.paintComponent(g);
					return;
				}
				else if (isModel) {
					if (getModel().isRollover() && !isSelected()) {
						img = modelButtonOverIcon;
					} else {
						img = isSelected()?modelButtonSelectedIcon:modelButtonIcon;
					}
				} else {
					if (getModel().isRollover() && !isSelected()) {
						img = gcodeButtonOverIcon;
					} else {
						img = isSelected()?gcodeButtonSelectedIcon:gcodeButtonIcon;
					}
				}
				g.drawImage(img, 0, 0, null);
				super.paintComponent(g);
			}

			public void buildElementUpdate(BuildElement element) {
				if (element.isModified()) {
					setText(build.get().getName()+"*");
					setFont(getFont().deriveFont(Font.BOLD));
				} else {
					setText(build.get().getName());
					setFont(getFont().deriveFont(Font.PLAIN));
				}
				repaint();
			}
			
		}
		
		public BuildElement getBuildElement() {
			Enumeration<AbstractButton> e = elementGroup.getElements();
			while (e.hasMoreElements()) {
				BuildElementButton beb = (BuildElementButton)e.nextElement();
				if (beb.isSelected()) { return beb.getBuildElement(); }
			}
			return null;
		}
		
		public TabButton(Build build) {
			this.build = new WeakReference<Build>(build);
			// setUI(new TabButtonUI());
			setBorder(new EmptyBorder(5,7,8,7));
			setLayout(new MigLayout("gap 0, ins 0", "push[right][right]"));
			tabGroup.add(this);
			addActionListener(EditorHeader.this);
			setOpaque(false);

			setText(build.getName());
			setHorizontalAlignment(SwingConstants.LEFT);

			Dimension d = super.getMinimumSize();
			setMinimumSize(new Dimension((int)d.getWidth() + 49, (int)d.getHeight()));
		    
			if (build.getModel() != null) {
				ElementButton eb = new ElementButton(build.getModel());
				this.add(eb, "growx");
				if (build.getOpenedElement() == build.getModel()) { eb.doClick(); } 
			} else {
				// Add a "fake" button that drwas transparent
				ElementButton eb = new ElementButton(/*isModel = */ true);
				this.add(eb, "growx");
			}
			
			if (build.getCode() != null) {
				ElementButton eb = new ElementButton(build.getCode());
				this.add(eb, "width 22!");
				if (build.getOpenedElement() == build.getModel()) { eb.doClick(); } 
			} else {
				// Add a "fake" button that drwas transparent
				ElementButton eb = new ElementButton(/*isModel = */ false);
				this.add(eb, "growx");
			}
		}
		
		protected void paintComponent(Graphics g) {
			initTabImages();
			BufferedImage img = isSelected()?selectedTabBg:regularTabBg;
			final int partWidth = img.getWidth()/3;
			int height = img.getHeight();
			final int x = 0;
			final int y = 0;
			final int w = getWidth();
			// Draw left side of tab
			g.drawImage(img, x, y, x+partWidth, y+height, 0, 0, partWidth, height, null);
			final int rightTabStart = img.getWidth()-partWidth;
			// Draw center of tab
			g.drawImage(img, x+partWidth, y, x+w-partWidth, y+height, partWidth, 0, rightTabStart, height, null);
			// Draw right side of tab
			g.drawImage(img, x+w-partWidth, y, x+w, y+height, rightTabStart, 0, img.getWidth(), height, null);
			setForeground(isSelected()?textSelectedColor:textUnselectedColor);
			super.paintComponent(g);
		}

		public void buildElementUpdate(BuildElement element) {
			if (element.isModified()) {
				setText(build.get().getName()+"*");
				setFont(getFont().deriveFont(Font.BOLD));
			} else {
				setText(build.get().getName());
				setFont(getFont().deriveFont(Font.PLAIN));
			}
			repaint();
		}
	}
	
	//JLabel titleLabel = new JLabel("Untitled");
	
	MainWindow editor;

	int fontAscent;

	int menuLeft;

	int menuRight;

	public EditorHeader(MainWindow mainWindow) {
		initTabImages();
		// setBorder(null);
		setLayout(new MigLayout("ins 0 10 0 10,gap 10 10 0 0"));
		this.editor = mainWindow;

		// add(titleLabel);
		// backgroundColor = new Color(0xFF, 0xFF, 0x00); //new Color(0x92, 0xA0, 0x6B);
		// backgroundImg = Base.getImage("images/background-disconnected.png", this);
		// vOffset = -40;

		textSelectedColor = new Color(0x00, 0x00, 0x00);
		textUnselectedColor = new Color(0x55, 0x55, 0x55);
		backgroundColor = new Color(0x00, 0xFF, 0xFF, 0x25); //new Color(0x92, 0xA0, 0x6B);
		setBackground(null); //backgroundColor
		setPreferredSize(new Dimension(750,29));
		
		setOpaque(false);
	}

	private void removeTabs() {
		tabGroup = new ButtonGroup();
		for (int i = 0; i < getComponentCount(); i++) {
			if (getComponent(i) instanceof TabButton) {
				remove(i);
				removeTabs();
				return;
			}
		}
		validate();
	}

	private void addTabForBuild(Build build) {
		TabButton tb = new TabButton(build);
		add(tb);
		tb.doClick();
		// if (build.getOpenedElement() == element) { tb.doClick(); } 
	}
	
	void setBuild(Build build) {
		int lines = 0;
		removeTabs();
		addTabForBuild(build);
		// titleLabel.setText(build.getName());
		// titleLabel.setToolTipText("lines: "+lines);
		validate();
		repaint();
	}

	public void actionPerformed(ActionEvent a) {
		ChangeEvent e = new ChangeEvent(this);
		if (changeListener != null) changeListener.stateChanged(e);
	}
}
