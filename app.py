from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Menghubungkan ke MongoDB
try:
    # Inisialisasi klien MongoDB dengan URL koneksi yang diberikan
    client = MongoClient("mongodb://localhost:27017/")  # Sesuaikan URL MongoDB jika diperlukan
    db = client.utsiot116  # Terhubung ke database yang ditentukan
    collection = db.data_sensor  # Menentukan koleksi di dalam database
    print("Terhubung ke MongoDB")  # Cetak pesan keberhasilan jika koneksi berhasil
except Exception as e:
    # Cetak pesan kesalahan jika koneksi ke MongoDB gagal
    print(f"Kesalahan saat menghubungkan ke MongoDB: {e}")

# Mendefinisikan rute utama yang menampilkan halaman beranda
@app.route('/')
def index():
    return render_template('home.html')  # Menampilkan template 'home.html'

# Mendefinisikan rute untuk menerima data sensor melalui permintaan POST
@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json  # Mengambil data JSON dari permintaan
    print(f"Data diterima: {data}")

    # Memeriksa apakah data yang diterima berisi kolom-kolom yang dibutuhkan
    if not data or 'suhumax' not in data or 'suhumin' not in data or 'suhurata2' not in data or 'nilaisuhuhumid' not in data or 'month_year' not in data:
        # Jika ada kolom yang diperlukan tidak ada, mengembalikan respons error
        return jsonify({"error": "Format data tidak valid. Kolom yang diperlukan: suhumax, suhumin, suhurata2, nilaisuhuhumid, month_year."}), 400

    # Menyimpan data yang diterima ke MongoDB
    try:
        collection.insert_one(data)  # Menyisipkan data ke MongoDB
        print(f"Data disimpan: {data}")  # Cetak pesan keberhasilan
        return jsonify({"message": "Data diterima dan disimpan dengan sukses"}), 200  # Mengembalikan respons sukses
    except Exception as e:
        # Cetak pesan kesalahan jika penyimpanan data gagal dan mengembalikan respons error
        print(f"Kesalahan saat memasukkan data: {e}")
        return jsonify({"error": "Gagal menyimpan data di MongoDB"}), 500

# Rute untuk mengambil data dari MongoDB
@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        # Mengambil data dari MongoDB, memilih kolom-kolom tertentu dan mengecualikan '_id'
        data = list(collection.find({}, {"_id": 0, "suhumax": 1, "suhumin": 1, "suhurata2": 1, "nilaisuhuhumid": 1, "month_year": 1}))

        # Memeriksa jika data ada; jika tidak, mengembalikan pesan yang menunjukkan tidak ada data
        if not data:
            return jsonify({"message": "Tidak ada data ditemukan"}), 404

        # Memformat data yang diambil untuk frontend
        formatted_data = [{
            'suhumax': item['suhumax'],
            'suhumin': item['suhumin'],
            'suhurata2': item['suhurata2'],
            'nilaisuhuhumid': item['nilaisuhuhumid'],
            'month_year': item['month_year']
        } for item in data]

        print(f"Data yang diambil: {formatted_data}")  # Cetak data yang diambil untuk verifikasi
        return jsonify(formatted_data), 200  # Mengirim data yang diformat sebagai respons JSON
    except Exception as e:
        # Cetak pesan kesalahan jika pengambilan data gagal dan mengembalikan respons error
        print(f"Kesalahan saat mengambil data: {e}")
        return jsonify({"error": "Gagal mengambil data dari MongoDB"}), 500

# Menjalankan aplikasi Flask dengan debug diaktifkan, dapat diakses dari semua antarmuka jaringan
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
