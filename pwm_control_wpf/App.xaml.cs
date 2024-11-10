using CoordinateSystem;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Windows;

namespace pwm_control_wpf
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            var mainWindow = new MainWindow();

            // Pass the command-line arguments to MainWindow
            if (e.Args.Length > 0)
            {
                mainWindow.PrepareDotsFromArguments(e.Args);
            }

            mainWindow.Show();
        }
    }
}
