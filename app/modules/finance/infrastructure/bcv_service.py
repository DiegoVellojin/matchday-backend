import pybcv
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from app.modules.matches.infrastructure.orm_models import TasaCambioORM
from decimal import Decimal

logger = logging.getLogger(__name__)

class BCVService:
    """
    Servicio de Sincronización Financiera.
    Centraliza la captura de tasas oficiales del Banco Central de Venezuela.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.bcv = pybcv.Currency()

    def sync_rates(self):
        """
        Consulta las tasas de USD y EUR y las persiste en la base de datos.
        Implementa resiliencia ante fallos de conexión y evita consultas redundantes.
        """
        # 1. Verificar si ya tenemos tasas recientes (menos de 2 horas)
        # Esto optimiza el arranque en plataformas como Render (Free Tier)
        latest = self.db.query(TasaCambioORM).order_by(TasaCambioORM.fecha_captura.desc()).first()
        if latest:
            diff = datetime.now() - latest.fecha_captura
            if diff.total_seconds() < 7200: # 2 horas
                logger.info("Las tasas son recientes (menos de 2h). Saltando sincronización externa.")
                return

        currencies = ["USD", "EUR"]
        
        for symbol in currencies:
            try:
                # Captura de tasa oficial
                rate_data = self.bcv.get_rate(symbol)
                # pybcv devuelve un float, convertimos a Decimal para precisión industrial
                monto_bs = Decimal(str(rate_data))
                
                # Crear registro histórico
                nueva_tasa = TasaCambioORM(
                    moneda=symbol,
                    monto_bs=monto_bs,
                    fuente="BCV",
                    fecha_captura=datetime.now()
                )
                
                self.db.add(nueva_tasa)
                logger.info(f"Sincronización exitosa: {symbol} -> {monto_bs} Bs.")
                
            except Exception as e:
                logger.warning(f"Error al sincronizar tasa {symbol} desde BCV: {str(e)}")
                # Continuamos con la siguiente moneda si una falla
                continue
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al persistir tasas en la base de datos: {str(e)}")

    def get_latest_rates(self):
        """
        Obtiene las tasas más recientes persistidas en la base de datos.
        Este método no consulta internet, garantizando alta disponibilidad.
        """
        rates = {}
        for symbol in ["USD", "EUR"]:
            tasa = self.db.query(TasaCambioORM)\
                .filter(TasaCambioORM.moneda == symbol)\
                .order_by(TasaCambioORM.fecha_captura.desc())\
                .first()
            
            if tasa:
                rates[symbol] = {
                    "monto_bs": float(tasa.monto_bs),
                    "fecha_referencia": tasa.fecha_referencia.isoformat(),
                    "fecha_captura": tasa.fecha_captura.isoformat()
                }
        return rates
