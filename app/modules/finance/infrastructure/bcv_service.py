import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any

import pyBCV as pybcv
from sqlalchemy.orm import Session

from app.modules.matches.infrastructure.orm_models import TasaCambioORM

logger = logging.getLogger(__name__)

class BCVService:
    """
    Servicio de Sincronización Financiera.
    Centraliza la captura de tasas oficiales del Banco Central de Venezuela.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.bcv = pybcv.Currency()

    def _parse_bcv_date(self, date_str: str) -> date:
        """
        Parsea la fecha devuelta por pyBCV (ej. "Viernes, 15 de mayo de 2026")
        a un objeto date nativo de Python de forma segura e independiente del locale.
        """
        MESES = {
            "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
            "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
            "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
        }
        try:
            # Limpieza del string: "Viernes, 15 de mayo de 2026" -> ["viernes", "15", "de", "mayo", "de", "2026"]
            parts = date_str.lower().replace(",", "").split()
            day = int(parts[1])
            month_str = parts[3]
            year = int(parts[5])
            
            month = MESES.get(month_str, datetime.now().month)
            return date(year, month, day)
        except Exception as e:
            logger.error(f"Error al parsear la fecha del BCV '{date_str}': {e}. Usando fecha actual como fallback.")
            return datetime.now().date()

    def sync_rates(self):
        """
        Consulta las tasas oficiales y las persiste en la base de datos.
        Implementa resiliencia ante fallos de conexión y extrae la fecha valor real.
        """
        # 1. Verificar si ya tenemos tasas recientes (menos de 2 horas)
        latest = self.db.query(TasaCambioORM).order_by(TasaCambioORM.fecha_captura.desc()).first()
        if latest:
            diff = datetime.now() - latest.fecha_captura
            if diff.total_seconds() < 7200: # 2 horas
                logger.info("Las tasas son recientes (menos de 2h). Saltando sincronización externa.")
                return

        try:
            # 2. Captura optimizada: Pedimos todo el diccionario en una sola petición HTTP
            all_rates = self.bcv.get_rate()
            fecha_bcv_str = all_rates.get("Fecha", "")
            fecha_referencia = self._parse_bcv_date(fecha_bcv_str)
        except Exception as e:
            logger.error(f"Fallo crítico al conectar con el portal del BCV: {e}")
            return

        currencies = ["USD", "EUR"]
        
        for symbol in currencies:
            if symbol in all_rates:
                try:
                    monto_bs = Decimal(str(all_rates[symbol]))
                    
                    # Crear registro histórico mapeando correctamente la fecha del BCV
                    nueva_tasa = TasaCambioORM(
                        moneda=symbol,
                        monto_bs=monto_bs,
                        fuente="BCV",
                        fecha_referencia=fecha_referencia,
                        fecha_captura=datetime.now()
                    )
                    
                    self.db.add(nueva_tasa)
                    logger.info(f"Sincronización exitosa: {symbol} -> {monto_bs} Bs. (Fecha Valor: {fecha_referencia})")
                    
                except Exception as e:
                    logger.warning(f"Error al procesar la tasa {symbol}: {str(e)}")
                    continue
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error al persistir tasas en la base de datos: {str(e)}")

    def get_latest_rates(self) -> Dict[str, Any]:
        """
        Obtiene las tasas legalmente vigentes para el día de hoy.
        Filtra tasas futuras (ej. publicadas el viernes para el lunes) durante el fin de semana.
        """
        rates = {}
        hoy = datetime.now().date()
        
        for symbol in ["USD", "EUR"]:
            # FILTRO CLAVE: fecha_referencia <= hoy asegura el cobro correcto los fines de semana
            tasa = self.db.query(TasaCambioORM)\
                .filter(
                    TasaCambioORM.moneda == symbol,
                    TasaCambioORM.fecha_referencia <= hoy
                )\
                .order_by(TasaCambioORM.fecha_referencia.desc(), TasaCambioORM.fecha_captura.desc())\
                .first()
            
            if tasa:
                rates[symbol] = {
                    "monto_bs": float(tasa.monto_bs),
                    "fecha_referencia": tasa.fecha_referencia.isoformat(),
                    "fecha_captura": tasa.fecha_captura.isoformat()
                }
        return rates