from app import db

class Transaksi(db.Model):
    __tablename__ = 'transaksi'

    id = db.Column(db.Integer, primary_key=True)
    id_pelanggan = db.Column(db.Integer, db.ForeignKey('pelanggan.id', ondelete='CASCADE'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    tipe = db.Column(db.Enum('topup', 'pembelian'), nullable=False)
    nominal = db.Column(db.Numeric(10, 2), nullable=False)
    keterangan = db.Column(db.String(255))
    waktu_transaksi = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Transaksi {self.id} ({self.tipe}) Rp{self.nominal}>"
