using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Shapes;
using System;

namespace CoordinateSystem
{
    public partial class MainWindow : Window
    {
        private Ellipse selectedDot = null;
        private Point offset;
        private const double xTickSpacing = 50; // Spacing between ticks for the X-axis in pixels, representing 2 units
        private const double yTickSpacing = 50; // Spacing between ticks for the Y-axis in pixels, representing 10 units
        private const double axisPadding = 30;  // Padding for axis labels

        // Store the logical positions of dots in the coordinate system
        private List<Point> dotPositions = new List<Point>();
        private List<Ellipse> dots = new List<Ellipse>();  // Store the dots
        private List<Line> lines = new List<Line>(); // Store the lines connecting dots

        public MainWindow()
        {
            InitializeComponent();
        }

        private void TitleBar_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.ButtonState == MouseButtonState.Pressed)
            {
                this.DragMove();
            }
        }

        private void Minimize_Click(object sender, RoutedEventArgs e)
        {
            this.WindowState = WindowState.Minimized;
        }

        private void Maximize_Click(object sender, RoutedEventArgs e)
        {
            if (this.WindowState == WindowState.Maximized)
            {
                this.WindowState = WindowState.Normal;
            }
            else
            {
                this.WindowState = WindowState.Maximized;
            }
        }

        private void Close_Click(object sender, RoutedEventArgs e)
        {
            this.Close();
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            ExportDotsToJson();
        }

        private void ExportDotsToJson()
        {
            var dotDictionary = new Dictionary<double, double>();

            foreach (var position in dotPositions)
            {
                dotDictionary[Math.Round(position.X, 0)] = Math.Round(position.Y, 0);
            }

            var json = JsonSerializer.Serialize(dotDictionary, new JsonSerializerOptions { WriteIndented = true });

            // Save the JSON to a file
            File.WriteAllText("temps.json", json);
        }

        public void PrepareDotsFromArguments(string[] args)
        {
            // Ensure there are an even number of arguments (pairs of x, y)
            if (args.Length % 2 != 0)
            {
                MessageBox.Show("Invalid number of arguments. Arguments should be pairs of x and y values.");
                return;
            }

            for (int i = 0; i < args.Length; i += 2)
            {
                if (double.TryParse(args[i], out double x) && double.TryParse(args[i + 1], out double y))
                {
                    // Ensure that the arguments are valid logical coordinates
                    if (x < 0 || y < 0)
                    {
                        MessageBox.Show("X and Y values must be non-negative.");
                        continue;
                    }

                    // Add the dot
                    AddDotToCanvas(x, y);
                }
                else
                {
                    MessageBox.Show($"Invalid argument at position {i} or {i + 1}");
                }
            }

            // Redraw lines to connect dots
            RedrawLines();
        }

        private void AddDotToCanvas(double logicalX, double logicalY)
        {
            // Convert logical coordinates to pixel coordinates
            double xPosition = axisPadding + (logicalX / 2) * xTickSpacing;
            double yPosition = DrawingCanvas.ActualHeight - axisPadding - (logicalY / 10) * yTickSpacing;

            // Create and place the dot
            Ellipse dot = new Ellipse
            {
                Width = 10,
                Height = 10,
                Fill = Brushes.Red
            };

            dotPositions.Add(new Point(logicalX, logicalY));
            dots.Add(dot);

            Canvas.SetLeft(dot, xPosition - dot.Width / 2);
            Canvas.SetTop(dot, yPosition - dot.Height / 2);
            DrawingCanvas.Children.Add(dot);

            // Attach right-click event handler to the dot
            dot.MouseRightButtonDown += Dot_MouseRightButtonDown;
        }

        private void Canvas_Loaded(object sender, RoutedEventArgs e)
        {
            DrawCoordinateSystem();
        }

        private void Canvas_SizeChanged(object sender, SizeChangedEventArgs e)
        {
            DrawCoordinateSystem();
        }

        private void DrawCoordinateSystem()
        {
            // Clear everything
            DrawingCanvas.Children.Clear();

            // Draw the axes
            XAxis.X1 = axisPadding;
            XAxis.Y1 = DrawingCanvas.ActualHeight - axisPadding;
            XAxis.X2 = DrawingCanvas.ActualWidth;
            XAxis.Y2 = DrawingCanvas.ActualHeight - axisPadding;

            YAxis.X1 = axisPadding;
            YAxis.Y1 = 0;
            YAxis.X2 = axisPadding;
            YAxis.Y2 = DrawingCanvas.ActualHeight - axisPadding;

            DrawingCanvas.Children.Add(XAxis);
            DrawingCanvas.Children.Add(YAxis);

            // Draw grid lines and labels for X axis (steps of 2 units)
            for (double i = 0, unit = 0; i < DrawingCanvas.ActualWidth - axisPadding; i += xTickSpacing, unit += 2)
            {
                double x = axisPadding + i;
                DrawGridLine(x, 0, x, DrawingCanvas.ActualHeight);
                DrawTick(x, DrawingCanvas.ActualHeight - axisPadding, true);
                DrawLabel(x - 9, DrawingCanvas.ActualHeight - axisPadding + 5, unit);
            }

            // Draw grid lines and labels for Y axis (steps of 10 units)
            for (double i = 0, unit = 0; i < DrawingCanvas.ActualHeight - axisPadding; i += yTickSpacing, unit += 10)
            {
                double y = DrawingCanvas.ActualHeight - axisPadding - i;
                DrawGridLine(0, y, DrawingCanvas.ActualWidth, y);
                DrawTick(axisPadding, y, false);
                DrawLabel(axisPadding - 25, y - 9, unit);
            }

            // Re-add the dots at their correct positions
            for (int i = 0; i < dots.Count; i++)
            {
                var dot = dots[i];
                var logicalPosition = dotPositions[i];

                // Convert logical coordinates back to pixel positions
                double xPosition = axisPadding + (logicalPosition.X / 2) * xTickSpacing;  // Divide by 2 for correct scaling
                double yPosition = DrawingCanvas.ActualHeight - axisPadding - (logicalPosition.Y / 10) * yTickSpacing;  // Divide by 10 for correct scaling

                Canvas.SetLeft(dot, xPosition - dot.Width / 2);
                Canvas.SetTop(dot, yPosition - dot.Height / 2);

                DrawingCanvas.Children.Add(dot);
            }

            // Re-add the lines connecting the dots
            RedrawLines();
        }

        private void DrawGridLine(double x1, double y1, double x2, double y2)
        {
            Line gridLine = new Line
            {
                X1 = x1,
                Y1 = y1,
                X2 = x2,
                Y2 = y2,
                Stroke = Brushes.LightGray,
                StrokeThickness = 0.5
            };
            DrawingCanvas.Children.Add(gridLine);
        }

        private void DrawTick(double x, double y, bool isHorizontal)
        {
            Line tick = new Line
            {
                Stroke = Brushes.Black,
                StrokeThickness = 1
            };

            if (isHorizontal)
            {
                tick.X1 = x;
                tick.Y1 = y - 5;
                tick.X2 = x;
                tick.Y2 = y + 5;
            }
            else
            {
                tick.X1 = x - 5;
                tick.Y1 = y;
                tick.X2 = x + 5;
                tick.Y2 = y;
            }

            DrawingCanvas.Children.Add(tick);
        }

        private void DrawLabel(double x, double y, double value)
        {
            TextBlock label = new TextBlock
            {
                Text = value.ToString(),
                FontSize = 12,
                Foreground = Brushes.Black
            };

            Canvas.SetLeft(label, x);
            Canvas.SetTop(label, y);

            DrawingCanvas.Children.Add(label);
        }

        private void Canvas_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (e.OriginalSource is Ellipse)
            {
                selectedDot = e.OriginalSource as Ellipse;
                offset = e.GetPosition(DrawingCanvas);
                offset.X -= Canvas.GetLeft(selectedDot);
                offset.Y -= Canvas.GetTop(selectedDot);
                DrawingCanvas.CaptureMouse();
            }
            else
            {
                Point clickPosition = e.GetPosition(DrawingCanvas);

                // Ensure the dot is placed within the coordinate system
                if (clickPosition.X < axisPadding || clickPosition.Y > DrawingCanvas.ActualHeight - axisPadding)
                    return;

                // Convert pixel position to logical position
                double logicalX = ((clickPosition.X - axisPadding) / xTickSpacing) * 2;  // Multiply by 2 for correct scaling
                double logicalY = ((DrawingCanvas.ActualHeight - clickPosition.Y - axisPadding) / yTickSpacing) * 10;  // Multiply by 10 for correct scaling

                // Check against the last placed dot
                if (dotPositions.Count > 0)
                {
                    var lastPosition = dotPositions.Last();
                    if (logicalX < lastPosition.X)
                    {
                        logicalX = lastPosition.X;
                    }

                    if (logicalY < lastPosition.Y)
                    {
                        logicalY = lastPosition.Y;
                    }
                }

                // Convert the adjusted logical position back to pixel position
                double xPosition = axisPadding + (logicalX / 2) * xTickSpacing;
                double yPosition = DrawingCanvas.ActualHeight - axisPadding - (logicalY / 10) * yTickSpacing;

                // Create a new dot
                Ellipse dot = new Ellipse
                {
                    Width = 10,
                    Height = 10,
                    Fill = Brushes.Red
                };

                dotPositions.Add(new Point(logicalX, logicalY));
                dots.Add(dot);

                Canvas.SetLeft(dot, xPosition - dot.Width / 2);
                Canvas.SetTop(dot, yPosition - dot.Height / 2);
                DrawingCanvas.Children.Add(dot);

                // Attach right-click event handler to the dot
                dot.MouseRightButtonDown += Dot_MouseRightButtonDown;

                // Redraw lines to connect dots
                RedrawLines();
            }
        }


        private void Dot_MouseRightButtonDown(object sender, MouseButtonEventArgs e)
        {
            if (sender is Ellipse dot)
            {
                int index = dots.IndexOf(dot);
                if (index >= 0)
                {
                    dotPositions.RemoveAt(index);
                    dots.RemoveAt(index);
                    DrawingCanvas.Children.Remove(dot);

                    // Redraw lines after removing a dot
                    RedrawLines();
                }
            }
        }

        private void Canvas_MouseMove(object sender, MouseEventArgs e)
        {
            if (selectedDot != null && e.LeftButton == MouseButtonState.Pressed)
            {
                Point currentPosition = e.GetPosition(DrawingCanvas);

                // Ensure the dot stays within the coordinate system
                if (currentPosition.X < axisPadding || currentPosition.Y > DrawingCanvas.ActualHeight - axisPadding)
                    return;

                // Calculate the new logical position
                double logicalX = ((currentPosition.X - offset.X + selectedDot.Width / 2 - axisPadding) / xTickSpacing) * 2;
                double logicalY = ((DrawingCanvas.ActualHeight - (currentPosition.Y - offset.Y + selectedDot.Height / 2) - axisPadding) / yTickSpacing) * 10;

                // Check against the previous and next dots in the sequence
                int index = dots.IndexOf(selectedDot);
                if (index > 0)
                {
                    var prevPosition = dotPositions[index - 1];
                    if (logicalX < prevPosition.X)
                    {
                        logicalX = prevPosition.X; // Prevent moving below the previous dot's x
                    }
                    if (logicalY < prevPosition.Y)
                    {
                        logicalY = prevPosition.Y; // Prevent moving below the previous dot's y
                    }
                }
                if (index < dotPositions.Count - 1)
                {
                    var nextPosition = dotPositions[index + 1];
                    if (logicalX > nextPosition.X)
                    {
                        logicalX = nextPosition.X; // Prevent moving above the next dot's x
                    }
                    if (logicalY > nextPosition.Y)
                    {
                        logicalY = nextPosition.Y; // Prevent moving above the next dot's y
                    }
                }

                // Convert the adjusted logical position back to pixel position
                double xPosition = axisPadding + (logicalX / 2) * xTickSpacing;
                double yPosition = DrawingCanvas.ActualHeight - axisPadding - (logicalY / 10) * yTickSpacing;

                // Move the dot
                Canvas.SetLeft(selectedDot, xPosition - selectedDot.Width / 2);
                Canvas.SetTop(selectedDot, yPosition - selectedDot.Height / 2);

                // Update the logical position of the selected dot
                dotPositions[index] = new Point(logicalX, logicalY);

                // Redraw lines to connect dots
                RedrawLines();
            }
        }


        private void Canvas_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
        {
            if (selectedDot != null)
            {
                DrawingCanvas.ReleaseMouseCapture();
                selectedDot = null;
            }
        }

        private void RedrawLines()
        {
            // Clear existing lines
            foreach (var line in lines)
            {
                DrawingCanvas.Children.Remove(line);
            }
            lines.Clear();

            // Sort dots by X position
            var sortedDots = dots.Select((dot, index) => new { Dot = dot, Position = dotPositions[index] })
                                 .OrderBy(d => d.Position.X)
                                 .ToList();

            // Draw lines connecting each dot to its two nearest neighbors on the X-axis
            for (int i = 0; i < sortedDots.Count; i++)
            {
                var currentDot = sortedDots[i];

                if (i > 0)
                {
                    var previousDot = sortedDots[i - 1];
                    lines.Add(DrawLineBetweenDots(previousDot.Dot, currentDot.Dot));
                }

                if (i < sortedDots.Count - 1)
                {
                    var nextDot = sortedDots[i + 1];
                    lines.Add(DrawLineBetweenDots(currentDot.Dot, nextDot.Dot));
                }
            }
        }

        private Line DrawLineBetweenDots(Ellipse dot1, Ellipse dot2)
        {
            var line = new Line
            {
                X1 = Canvas.GetLeft(dot1) + dot1.Width / 2,
                Y1 = Canvas.GetTop(dot1) + dot1.Height / 2,
                X2 = Canvas.GetLeft(dot2) + dot2.Width / 2,
                Y2 = Canvas.GetTop(dot2) + dot2.Height / 2,
                Stroke = Brushes.Red,
                StrokeThickness = 2
            };

            DrawingCanvas.Children.Add(line);
            return line;
        }
    }
}
