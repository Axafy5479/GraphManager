using System;
using System.Collections.Generic;
using System.Collections.Specialized;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using Microsoft.Web.WebView2.Wpf;

namespace GraphDrawer
{

    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private string binaryPath = "";
        private string uuid = "";
        private string tempPngName = "temp.png";
        private bool debugMode = false;
        TabControl tabCtrl = null;
        Task eventLoop = null;

        public MainWindow()
        {
            InitializeComponent();
            Loaded += (s, e)=>Run();
            Closed += (s, e) => OnQuit();
        }

        private void OnQuit()
        {
            string tempPath = uuid == ""
                ? Path.Combine(binaryPath, "temp")
                : Path.Combine(binaryPath, @$"temp\{uuid}");

            if (Directory.Exists(tempPath))
            {
                Directory.Delete(tempPath, recursive: true);
            }

        }

        private async Task Run()
        {


            try
            {


                binaryPath = Directory.GetParent(Assembly.GetEntryAssembly().Location).FullName;
                Task task = null;

                if (debugMode)
                {
                    uuid = Guid.NewGuid().ToString();
                    task = InitializeWebView(uuid);
                }
                else if (System.Environment.GetCommandLineArgs()[1] == "showHTML")
                {
                    uuid = System.Environment.GetCommandLineArgs()[2];
                    task = InitializeWebView(uuid);
                }
                else if(System.Environment.GetCommandLineArgs()[1] == "showTabView")
                {
                    uuid = System.Environment.GetCommandLineArgs()[2];
                    var parent = (Grid)FindName("parentGrid");
                    tabCtrl = new TabControl();
                    parent.Children.Add(tabCtrl);

                    var files = Directory.GetFiles(Path.Combine(binaryPath, "temp\\" + uuid));
                    eventLoop = Update(binaryPath + "\\temp\\" + uuid);
                    int tabNumber = files.Length;
                    var tasks = new List<Task>();


                    for (int i = 0; i < tabNumber; i++)
                    {
                        var tabItem = new TabItem();
                        tabCtrl.Items.Add(tabItem);

                        string fileName = Array.Find(files, s => s.Contains("temp" + i));
                        var tabNameTempArray = fileName.Split("\\");
                        var tabNameTemp = tabNameTempArray[tabNameTempArray.Length - 1].Replace("temp" + i + "___tab-", "");
                        tabItem.Header = tabNameTemp.Replace(".html", "");

                        var wv = new WebView2();
                            eventLoop = Update(binaryPath + "\\temp\\" + Environment.GetCommandLineArgs()[2]);
                        tasks.Add(InitializeWebView(wv, fileName));
                        tabItem.Content = wv;
                    }
                    task = Task.WhenAll(tasks);
                }
                else
                {
                    uuid = Guid.NewGuid().ToString();
                    string path = System.Environment.GetCommandLineArgs()[1];
                    if (System.IO.Path.GetExtension(path) == ".sun")
                    {
                        task = Task.WhenAll(InitializeWebView(uuid), _ShowSingleGraph(uuid));
                    }
                    else if (System.IO.Path.GetExtension(path) == ".sunny")
                    {
                        await _ShowTabGraph(uuid);

                        var parent = (Grid)FindName("parentGrid");
                        tabCtrl = new TabControl();
                        parent.Children.Add(tabCtrl);

                        var files = Directory.GetFiles(Path.Combine(binaryPath, "temp\\"+uuid));
                        eventLoop = Update(binaryPath + "\\temp\\" + uuid);
                        int tabNumber = files.Length;
                        var tasks = new List<Task>();
                        for (int i = 0; i < tabNumber; i++)
                        {
                            var tabItem = new TabItem();
                            tabCtrl.Items.Add(tabItem);

                            string fileName = Array.Find(files, s => s.Contains("temp" + i));
                            var tabNameTempArray = fileName.Split("\\");
                            var tabNameTemp = tabNameTempArray[tabNameTempArray.Length - 1].Replace("temp" + i+"___tab-","");
                            tabItem.Header = tabNameTemp.Replace(".html","");
                            var wv = new WebView2();
                            tasks.Add(InitializeWebView(wv, fileName));
                            tabItem.Content = wv;
                        }
                        task = Task.WhenAll(tasks);
                        await task;

                    }
                }

                if(task!=null) await task;
            }
            catch (Exception ex)
            {
                using var sw = new StreamWriter("error_log.txt");
                sw.WriteLine(ex.Message);
                sw.WriteLine(ex.StackTrace);
                sw.WriteLine("Run");


                sw.WriteLine("受け取った引数は\n" + string.Join("\n", System.Environment.GetCommandLineArgs()));
            }
        }

        private async Task<string> _ShowSingleGraph(string uuid)
        {
            try
            {
                string myPythonApp = binaryPath + "\\GraphDrawingTool\\Draw.py";
                bool d = File.Exists(myPythonApp);

                ProcessStartInfo psInfo = new ProcessStartInfo();

                // 実行するファイルをセット
                psInfo.FileName = "Python";

                //引数をセット
                string fig_json = debugMode ? @"G:\マイドライブ\Experiment\Raman2\20230216\test.sun" : System.Environment.GetCommandLineArgs()[1];
                //fig_json = "G:\\マイドライブ\\Experiment\\Raman2\\20230216\\polystyrene_rayleigh_graph.sun";
                psInfo.Arguments = string.Format("\"{0}\" {1} {2} {3}", myPythonApp, fig_json, binaryPath, uuid);
                //"G:\\マイドライブ\\Experiment\\Raman2\\20230216\\polystyrene_rayleigh_graph.sun");

                // コンソール・ウィンドウを開かない
                psInfo.CreateNoWindow = true;

                // シェル機能を使用しない
                psInfo.UseShellExecute = false;

                // 標準出力をリダイレクトする
                psInfo.RedirectStandardOutput = true;
                psInfo.RedirectStandardInput = true;

                // プロセスを開始
                Process p = Process.Start(psInfo);
                //await p.WaitForExitAsync();

                // アプリのコンソール出力結果を全て受け取る
                string line = "";

                string l;
                while ((l = p.StandardOutput.ReadLine()) != null)
                {
                    line += l.Replace(" ", "");
                }
                return line;

            }
            catch (Exception ex)
            {
                using var sw = new StreamWriter("error_log.txt");
                sw.WriteLine(ex.Message);
                sw.WriteLine(ex.StackTrace);
                sw.WriteLine("_ShowSingleGraph");


                return ex.Message;
            }
        }

        private async Task<string> _ShowTabGraph(string uuid)
        {
            try
            {
                string myPythonApp = binaryPath + "\\GraphDrawingTool\\DrawTabGraph.py";
                bool d = File.Exists(myPythonApp);

                ProcessStartInfo psInfo = new ProcessStartInfo();

                // 実行するファイルをセット
                psInfo.FileName = "Python";

                //引数をセット
                string fig_json = debugMode ? @"G:\マイドライブ\Experiment\Raman2\20230216\test.sun" : System.Environment.GetCommandLineArgs()[1];
                //fig_json = "G:\\マイドライブ\\Experiment\\Raman2\\20230216\\polystyrene_rayleigh_graph.sun";
                psInfo.Arguments = string.Format("\"{0}\" {1} {2} {3}", myPythonApp, fig_json, binaryPath, uuid);
                //"G:\\マイドライブ\\Experiment\\Raman2\\20230216\\polystyrene_rayleigh_graph.sun");

                // コンソール・ウィンドウを開かない
                psInfo.CreateNoWindow = true;

                // シェル機能を使用しない
                psInfo.UseShellExecute = false;

                // 標準出力をリダイレクトする
                psInfo.RedirectStandardOutput = true;
                psInfo.RedirectStandardInput = true;

                // プロセスを開始
                Process p = Process.Start(psInfo);
                //await p.WaitForExitAsync();

                // アプリのコンソール出力結果を全て受け取る
                string line = "";

                string l;
                while ((l = p.StandardOutput.ReadLine()) != null)
                {
                    line += l.Replace(" ", "");
                }
                return line;

            }
            catch (Exception ex)
            {
                using var sw = new StreamWriter("error_log.txt");
                sw.WriteLine(ex.Message);
                sw.WriteLine(ex.StackTrace);
                sw.WriteLine("_ShowTabGraph");

                return ex.Message;
            }
        }


        private async Task InitializeWebView(string uuid)
        {
            try
            {
                var webView = new WebView2();
                var parent = (Grid)FindName("parentGrid");
                parent.Children.Add(webView);
                var path = binaryPath + "\\temp\\" + uuid + "\\temp.html";
                eventLoop = Update(binaryPath + "\\temp\\" + uuid);
                InitializeWebView(webView, path);
            }
            catch (Exception ex)
            {
                using var sw = new StreamWriter("error_log.txt");
                sw.WriteLine(ex.Message);
                sw.WriteLine(MethodInfo.GetCurrentMethod().Name);

                sw.WriteLine("受け取った引数は\n" + string.Join("\n", System.Environment.GetCommandLineArgs()));
            }
        }
        private async Task InitializeWebView(WebView2 webView, string htmlPath)
        {
            try
            {
                await webView.EnsureCoreWebView2Async();
                while (!File.Exists(htmlPath))
                {
                    await Task.Delay(50);
                }

                webView.Source = new Uri(htmlPath);
            }
            catch (Exception ex)
            {
                using var sw = new StreamWriter("error_log.txt");
                sw.WriteLine(ex.Message);
                sw.WriteLine("InitializeWebView");

                sw.WriteLine("受け取った引数は\n" + string.Join("\n", System.Environment.GetCommandLineArgs()));
            }
        }


        private void OnCtrlC(object sender, ExecutedRoutedEventArgs e)
        {
            CopyScreen();


        }

        private async Task CopyScreen()
        {
            using (MemoryStream ms = new MemoryStream())
            {

                try
                {
                    var webView = tabCtrl == null?((WebView2)FindName("wv")): (WebView2)(((TabItem)tabCtrl.SelectedItem).Content);

                    await webView.CoreWebView2.CapturePreviewAsync(Microsoft.Web.WebView2.Core.CoreWebView2CapturePreviewImageFormat.Png, ms);

                    var imageSource = new BitmapImage() { CacheOption = BitmapCacheOption.OnLoad };
                    imageSource.BeginInit();

                    imageSource.StreamSource = ms;
                    imageSource.EndInit();

                    CroppedBitmap chained = new CroppedBitmap(imageSource, new Int32Rect(10, 30, (int)imageSource.Width - 30, (int)imageSource.Height - 40));

                    Clipboard.SetImage(chained);
                }
                catch (Exception ex)
                {
                    using var sw = new StreamWriter("error_log.txt");
                    sw.WriteLine(ex.Message);
                    sw.WriteLine("CopyScreen");
                    sw.WriteLine("受け取った引数は\n" + string.Join("\n", System.Environment.GetCommandLineArgs()));
                }

            }
        }


        private void Checkbox_Clicked(object sender, RoutedEventArgs e)
        {
            Application.Current.MainWindow.Topmost = true;

        }

        private void Checkbox_UnChecked(object sender, RoutedEventArgs e)
        {
            Application.Current.MainWindow.Topmost = false;
        }

        private async Task Update(string dirPath)
        {
            while (true)
            {
                await Task.Delay(50);

                if(File.Exists(Path.Combine(dirPath, ".star")))
                {
                    File.Delete(Path.Combine(dirPath, ".star"));
                    var parent = (Grid)FindName("parentGrid");
                    parent.Children.Clear();
                    break;
                }
            }

            Run();
        }
    }
}
