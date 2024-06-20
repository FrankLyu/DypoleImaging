using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MySql.Data.MySqlClient;
using Enyim.Caching;
using Enyim.Caching.Configuration;
using System.IO;

namespace dbHelperNamespace
{
    public class dbHelperClass
    {

        public static void writeImageDataToDB(string memcachedServerIP, string MYSQLserverIP, string username, string password, string databaseName, Int16[] atoms, Int16[] noAtoms, Int16[] dark, int width, int height, int cameraID, int runID, int seqID)
        {

            MySqlConnection conn = null; //The connection
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            try
            {
                mcc.AddServer(memcachedServerIP + ":11211");
                mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
                client = new MemcachedClient(mcc);
            }
            catch
            {

            }

            try
            {

                string myConnectionString = "server=" + MYSQLserverIP + ";uid=" + username + ";" + "pwd=" + password + ";database=" + databaseName + ";";
                conn = new MySqlConnection(myConnectionString);
                try
                {
                    conn.Open();


                    MySqlCommand cmd1 = new MySqlCommand("INSERT INTO images (timestamp,runID_fk,sequenceID_fk,cameraID_fk,atoms,noAtoms,dark) VALUES(@timestamp,@runID,@sequenceID,@cameraID,@atoms, @noAtoms, @dark)", conn);
                    cmd1.Prepare();


                    byte[] bytesAtoms = new byte[2 * height * width];
                    byte[] bytesNoAtoms = new byte[2 * height * width];
                    byte[] bytesDark = new byte[2 * height * width];


                    //The conversion for loop below is actually slower. Don't forget this.
                    /*  for (int i = 0; i < atoms.GetLength(0); i++)
                      {
                          for (int j = 0; j < atoms.GetLength(1); j++)
                          {
                              Array.Copy(BitConverter.GetBytes(atoms[i, j]), 0, bytesAtoms, 2 * (j + width * i),2);
                              Array.Copy(BitConverter.GetBytes(noAtoms[i, j]), 0, bytesNoAtoms, 2 * (j + width * i), 2);
                              Array.Copy(BitConverter.GetBytes(dark[i, j]), 0, bytesDark,2 * (j + width * i), 2);

                          }
                      }*/


                    Buffer.BlockCopy(atoms, 0, bytesAtoms, 0, bytesAtoms.Length);
                    Buffer.BlockCopy(noAtoms, 0, bytesNoAtoms, 0, bytesNoAtoms.Length);
                    Buffer.BlockCopy(dark, 0, bytesDark, 0, bytesDark.Length);


                    cmd1.Parameters.AddWithValue("@atoms", bytesAtoms);
                    cmd1.Parameters.AddWithValue("@noAtoms", bytesNoAtoms);
                    cmd1.Parameters.AddWithValue("@dark", bytesDark);
                    cmd1.Parameters.AddWithValue("@runID", runID);
                    cmd1.Parameters.AddWithValue("@sequenceID", seqID);
                    cmd1.Parameters.AddWithValue("@cameraID", cameraID);
                    cmd1.Parameters.AddWithValue("@timestamp", DateTime.Now.ToString());

                    cmd1.ExecuteNonQuery();


                }
                catch (Exception ex)
                {
                    try { conn.Close(); }
                    catch (Exception) { };
                    conn = null;
                }
            }
            catch
            {
            }







        }
        public static void writeImageDataToCache(string memcachedServerIP, Int16[] atoms, Int16[] noAtoms, Int16[] dark, int width, int height, int cameraID, int runID, int seqID)
        {


            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            try
            {
                mcc.AddServer(memcachedServerIP + ":11211");
                mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
                client = new MemcachedClient(mcc);


                byte[] bytesAtoms = new byte[2 * width * height];
                byte[] bytesNoAtoms = new byte[2 * width * height];
                byte[] bytesDark = new byte[2 * width * height];


                Buffer.BlockCopy(atoms, 0, bytesAtoms, 0, bytesAtoms.Length);
                Buffer.BlockCopy(noAtoms, 0, bytesNoAtoms, 0, bytesNoAtoms.Length);
                Buffer.BlockCopy(dark, 0, bytesDark, 0, bytesDark.Length);

                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "atoms", bytesAtoms);
                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "noAtoms", bytesNoAtoms);
                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "dark", bytesDark);
                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "camID", cameraID);
                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "runID", runID);
                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "seqID", seqID);


            }
            catch
            {

            }
        }
        public static void checkIfVariablesHaveBeenUpdated(string memcachedServerIP, string MYSQLserverIP, string username, string password, string databaseName, Int16[] shot, int width, int height, int cameraID)
        {


            MySqlConnection conn = null; //The connection
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            try
            {
                mcc.AddServer(memcachedServerIP + ":11211");
                mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
                client = new MemcachedClient(mcc);



                byte[] bytes = new byte[2 * width * height];



                Buffer.BlockCopy(shot, 0, bytes, 0, bytes.Length);


                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "free", bytes);
                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "camID", cameraID);
                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "height", height);
                client.Store(Enyim.Caching.Memcached.StoreMode.Set, "width", width);


            }
            catch
            {

            }

            try
            {

                string myConnectionString = "server=" + MYSQLserverIP + ";uid=" + username + ";" + "pwd=" + password + ";database=" + databaseName + ";";
                conn = new MySqlConnection(myConnectionString);
                try
                {
                    conn.Open();
                }
                catch (Exception ex)
                {
                    try { conn.Close(); }
                    catch (Exception) { };
                    conn = null;
                }
            }
            catch
            {
            }




        }
        public static void updateNewImage(string memcachedServerIP, string MYSQLserverIP, string username, string password, string databaseName)
        {

            MySqlConnection conn = null; //The connection
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            try
            {
                mcc.AddServer(memcachedServerIP + ":11211");
                mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
                client = new MemcachedClient(mcc);
            }
            catch
            {

            }

            try
            {

                string myConnectionString = "server=" + MYSQLserverIP + ";uid=" + username + ";" + "pwd=" + password + ";database=" + databaseName + ";";
                conn = new MySqlConnection(myConnectionString);
                try
                {
                    conn.Open();


                    MySqlCommand cmd1 = new MySqlCommand("UPDATE updates SET newImage = 1 WHERE idupdates = 0", conn);
                    cmd1.ExecuteNonQuery();

                }
                catch (Exception ex)
                {
                    try { conn.Close(); }
                    catch (Exception) { };
                    conn = null;
                }
            }
            catch
            {
            }


        }
        public static void undoUpdateNewRun(string memcachedServerIP, string MYSQLserverIP, string username, string password, string databaseName)
        {

            MySqlConnection conn = null; //The connection
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            try
            {
                mcc.AddServer(memcachedServerIP + ":11211");
                mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
                client = new MemcachedClient(mcc);
            }
            catch
            {

            }

            try
            {

                string myConnectionString = "server=" + MYSQLserverIP + ";uid=" + username + ";" + "pwd=" + password + ";database=" + databaseName + ";";
                conn = new MySqlConnection(myConnectionString);
                try
                {
                    conn.Open();

                    MySqlCommand cmd1 = new MySqlCommand("UPDATE updates SET newRun = 0 WHERE idupdates = 0", conn);
                    cmd1.ExecuteNonQuery();

                }
                catch (Exception ex)
                {
                    try { conn.Close(); }
                    catch (Exception) { };
                    conn = null;
                }
            }
            catch
            {
            }




        }

        public static int getLastRunID(string memcachedServerIP, string MYSQLserverIP, string username, string password, string databaseName) //This should run when the table is, and then be kept in memory until an image arrives OR a new update occurs 
        {

            MySqlConnection conn = null; //The connection
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            try
            {
                mcc.AddServer(memcachedServerIP + ":11211");
                mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
                client = new MemcachedClient(mcc);
            }
            catch
            {

            }

            try
            {

                string myConnectionString = "server=" + MYSQLserverIP + ";uid=" + username + ";" + "pwd=" + password + ";database=" + databaseName + ";";
                conn = new MySqlConnection(myConnectionString);
                try
                {
                    conn.Open();

                    MySqlCommand cmd1 = new MySqlCommand("SELECT runID from ciceroOut ORDER BY runID DESC LIMIT 1", conn);
                    return (int)cmd1.ExecuteScalar();

                }
                catch (Exception ex)
                {
                    try { conn.Close(); }
                    catch (Exception) { };
                    conn = null;
                    return 0;
                }
            }
            catch
            {
                return 0;
            }



        }
        public static int getSequenceID(string memcachedServerIP, string MYSQLserverIP, string username, string password, string databaseName)//Likewise for this guy
        {

            MySqlConnection conn = null; //The connection
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            try
            {
                mcc.AddServer(memcachedServerIP + ":11211");
                mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
                client = new MemcachedClient(mcc);
            }
            catch
            {

            }

            try
            {

                string myConnectionString = "server=" + MYSQLserverIP + ";uid=" + username + ";" + "pwd=" + password + ";database=" + databaseName + ";";
                conn = new MySqlConnection(myConnectionString);
                try
                {
                    conn.Open();

                    MySqlCommand cmd1 = new MySqlCommand("SELECT sequenceID from sequence ORDER BY sequenceID DESC LIMIT 1", conn);
                    return (int)cmd1.ExecuteScalar();
                }
                catch (Exception ex)
                {
                    try { conn.Close(); }
                    catch (Exception) { };
                    conn = null;
                    return 0;
                }
            }
            catch
            {
                return 0;
            }




        }
        public static int checkForRunUpdate(string memcachedServerIP, string MYSQLserverIP, string username, string password, string databaseName)
        {

            MySqlConnection conn = null; //The connection
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            try
            {
                mcc.AddServer(memcachedServerIP + ":11211");
                mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
                client = new MemcachedClient(mcc);
            }
            catch
            {

            }

            try
            {

                string myConnectionString = "server=" + MYSQLserverIP + ";uid=" + username + ";" + "pwd=" + password + ";database=" + databaseName + ";";
                conn = new MySqlConnection(myConnectionString);
                try
                {
                    conn.Open();

                    MySqlCommand cmd1 = new MySqlCommand("SELECT newRun FROM updates", conn);
                    return (int)cmd1.ExecuteScalar();
                }
                catch (Exception ex)
                {
                    try { conn.Close(); }
                    catch (Exception) { };
                    conn = null;
                    return 0;
                }
            }
            catch
            {
                return 0;
            }



        }

        #region Test functions for Python
        public int Add(int a, int b)
        {
            return a + b;
        }

        public int Sub(int a, int b)
        {
            return a - b;
        }
        public Int16[] AddArray(Int16[] A, Int16[] B)
        {
            Int16[] C = new Int16[A.Length];
            for (int i = 0; i < A.Length; i++)
            {
                C[i] = (short)((short)A[i] + B[i]);
            }
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            mcc.AddServer("192.168.1.133" + ":11211");
            mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
            mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
            mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
            client = new MemcachedClient(mcc);

            byte[] bytesC = new byte[2 * C.Length];

            Buffer.BlockCopy(C, 0, bytesC, 0, bytesC.Length);

            client.Store(Enyim.Caching.Memcached.StoreMode.Set, "darkC", bytesC);

            byte[] retreivedC = (byte[])client.Get("darkC");

            Int16[] atoms = new Int16[C.Length];
            Buffer.BlockCopy(retreivedC, 0, atoms, 0, retreivedC.Length);

            return atoms;
        }

        public Int16[] ReadArray(string name)
        {
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            mcc.AddServer("192.168.1.133" + ":11211");
            mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
            mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
            mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
            client = new MemcachedClient(mcc);

            byte[] retreivedC = (byte[])client.Get(name);

            Int16[] atoms = new Int16[retreivedC.Length / 2];
            Buffer.BlockCopy(retreivedC, 0, atoms, 0, retreivedC.Length);

            return atoms;
        }
        public void WriteArray(Int16[] A)
        {
            string filePath = @"C:\Users\Dypole\Desktop\ImagingAndor\output.txt";
            string content = string.Join("", A);
            using (StreamWriter outputFile = new StreamWriter(filePath))
            {
                outputFile.WriteLine(content);
            }
        }

        public static int getLastRunID2()
        {
            string memcachedServerIP = "192.168.1.133";
            string MYSQLserverIP = "192.168.1.133";
            string username = "root";
            string password = "w0lfg4ng";
            string databaseName = "dypoledatabase";

            MySqlConnection conn = null; //The connection
            MemcachedClientConfiguration mcc = new MemcachedClientConfiguration();
            MemcachedClient client;
            try
            {
                mcc.AddServer(memcachedServerIP + ":11211");
                mcc.SocketPool.ReceiveTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.ConnectionTimeout = new TimeSpan(0, 0, 10);
                mcc.SocketPool.DeadTimeout = new TimeSpan(0, 0, 20);
                client = new MemcachedClient(mcc);
            }
            catch
            {

            }

            try
            {

                string myConnectionString = "server=" + MYSQLserverIP + ";uid=" + username + ";" + "pwd=" + password + ";database=" + databaseName + ";";
                conn = new MySqlConnection(myConnectionString);
                try
                {
                    conn.Open();

                    MySqlCommand cmd1 = new MySqlCommand("SELECT runID from ciceroOut ORDER BY runID DESC LIMIT 1", conn);
                    return (int)cmd1.ExecuteScalar();

                }
                catch (Exception ex)
                {
                    try { conn.Close(); }
                    catch (Exception) { };
                    conn = null;
                    return 0;
                }
            }
            catch
            {
                return 0;
            }



        }

        #endregion
    }
}
