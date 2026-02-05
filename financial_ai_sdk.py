"""
SDK de FinancialAI - Cliente Python para API de Análisis Financiero

Uso simple:
    ai = FinancialAI(api_url="http://localhost:5000", token="YOUR_TOKEN")
    result = ai.full_analysis()
"""

import requests
import json
from typing import Dict, Optional, List
from datetime import datetime
import time


class FinancialAIError(Exception):
    """Excepción base del SDK"""
    pass


class FinancialAI:
    """Cliente Python para acceder a los análisis financieros de IA"""
    
    def __init__(self, api_url: str, token: str, timeout: int = 30):
        """
        Inicializar el cliente
        
        Args:
            api_url: URL base de la API (ej: http://localhost:5000)
            token: Token JWT para autenticación
            timeout: Timeout en segundos para las requests
        """
        self.api_url = api_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Realizar una request a la API
        
        Args:
            method: GET, POST, etc
            endpoint: Ruta del endpoint (ej: /api/v2/analysis/full)
            **kwargs: Argumentos adicionales para requests
        
        Returns:
            Dict con la respuesta JSON
        
        Raises:
            FinancialAIError si hay error
        """
        url = f"{self.api_url}{endpoint}"
        
        try:
            kwargs.setdefault('headers', self.headers)
            kwargs.setdefault('timeout', self.timeout)
            
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('success', True):
                raise FinancialAIError(data.get('error', 'Error desconocido'))
            
            return data
        
        except requests.exceptions.ConnectionError:
            raise FinancialAIError(f"No se pudo conectar a {url}")
        except requests.exceptions.Timeout:
            raise FinancialAIError(f"Timeout en {url}")
        except requests.exceptions.HTTPError as e:
            raise FinancialAIError(f"Error HTTP {response.status_code}: {response.text}")
        except json.JSONDecodeError:
            raise FinancialAIError("Respuesta no válida del servidor")
    
    def quick_analysis(self) -> Dict:
        """
        Análisis rápido (< 2 segundos)
        
        Retorna:
            - prediccion: Predicciones rápidas
            - estadisticas: Estadísticas básicas
        
        Example:
            >>> ai = FinancialAI(api_url, token)
            >>> result = ai.quick_analysis()
            >>> print(result['data']['prediccion'])
        """
        return self._request('POST', '/api/v2/analysis/quick')
    
    def full_analysis(self) -> Dict:
        """
        Análisis completo (2-5 segundos)
        
        Retorna:
            - prediccion: Todas las predicciones
            - estadisticas: Análisis estadístico completo
            - ahorro: Recomendaciones de ahorro
            - graficos: Datos para gráficos
        
        Example:
            >>> result = ai.full_analysis()
            >>> prediction = result['data']['prediccion']
            >>> savings = result['data']['ahorro']
            >>> charts = result['data']['graficos']
        """
        return self._request('POST', '/api/v2/analysis/full')
    
    def queue_analysis(self, wait: bool = False, timeout: int = 60) -> Dict:
        """
        Encola un análisis profundo (asíncrono)
        
        Args:
            wait: Si es True, espera a que termine (con timeout)
            timeout: Tiempo máximo en segundos para esperar
        
        Returns:
            Si wait=False: {'job_id', 'status', 'estimated_time_seconds'}
            Si wait=True: Resultado completo del análisis
        
        Example:
            >>> # Asíncrono
            >>> result = ai.queue_analysis()
            >>> job_id = result['data']['job_id']
            >>> status = ai.check_job(job_id)
            
            >>> # Con espera
            >>> result = ai.queue_analysis(wait=True, timeout=120)
            >>> print(result['data']['resultado'])
        """
        response = self._request('POST', '/api/v2/analysis/queue')
        
        if not wait:
            return response
        
        job_id = response['data']['job_id']
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job_status = self.check_job(job_id)
            status = job_status['data']['status']
            
            if status == 'completed':
                return job_status
            elif status == 'error':
                raise FinancialAIError(job_status['data'].get('error', 'Error desconocido'))
            
            time.sleep(2)  # Esperar 2 segundos antes de reintentar
        
        raise FinancialAIError(f"Timeout esperando job {job_id}")
    
    def check_job(self, job_id: str) -> Dict:
        """
        Verificar el estado de un análisis en queue
        
        Args:
            job_id: ID del job retornado por queue_analysis()
        
        Returns:
            Estado del job y resultado si está completado
        
        Example:
            >>> job_id = "job_abc123"
            >>> status = ai.check_job(job_id)
            >>> print(status['data']['status'])  # 'queued', 'processing', 'completed'
        """
        return self._request('GET', f'/api/v2/analysis/job/{job_id}')
    
    def cancel_job(self, job_id: str) -> Dict:
        """
        Cancelar un análisis en queue
        
        Args:
            job_id: ID del job a cancelar
        """
        return self._request('DELETE', f'/api/v2/analysis/job/{job_id}')
    
    def predict_category(self) -> Dict:
        """Predicción por categoría (heredado, usa quick_analysis ahora)"""
        return self._request('GET', '/api/v2/predict-category')
    
    def predict_monthly(self) -> Dict:
        """Predicción mensual (heredado, usa quick_analysis ahora)"""
        return self._request('GET', '/api/v2/predict-monthly')
    
    def detect_anomalies(self) -> Dict:
        """Detección de anomalías (heredado, usa quick_analysis ahora)"""
        return self._request('GET', '/api/v2/detect-anomalies')
    
    def get_savings_tips(self) -> Dict:
        """Obtener tips de ahorro (heredado, usa full_analysis ahora)"""
        return self._request('GET', '/api/v2/savings/tips')
    
    def get_health_score(self) -> Dict:
        """Obtener puntuación financiera (heredado, usa full_analysis ahora)"""
        return self._request('GET', '/api/v2/savings/health-score')
    
    def get_charts_dashboard(self) -> Dict:
        """Obtener datos del dashboard (heredado, usa full_analysis ahora)"""
        return self._request('GET', '/api/v2/charts/dashboard')


class FinancialAIAnalyzer:
    """Analizador de resultados para FinancialAI"""
    
    def __init__(self, analysis_result: Dict):
        """
        Inicializar con resultado de análisis
        
        Args:
            analysis_result: Dict retornado por full_analysis()
        """
        self.data = analysis_result.get('data', {})
        self.meta = analysis_result.get('meta', {})
    
    def get_prediction_summary(self) -> str:
        """Resumen de predicciones en texto"""
        pred = self.data.get('prediccion', {})
        
        lines = ["📊 RESUMEN DE PREDICCIONES"]
        lines.append("-" * 40)
        
        if 'categoria' in pred:
            lines.append("Gastos por categoría (predicción):")
            for cat, amount in pred['categoria'].items():
                lines.append(f"  • {cat}: ${amount:.2f}")
        
        if 'anomalias' in pred:
            ano = pred['anomalias']
            lines.append(f"\nAnomalías detectadas: {ano.get('detectadas', 0)}")
            lines.append(f"Porcentaje: {ano.get('porcentaje', 0):.1f}%")
        
        return "\n".join(lines)
    
    def get_savings_summary(self) -> str:
        """Resumen de oportunidades de ahorro"""
        savings = self.data.get('ahorro', {})
        
        lines = ["💰 RESUMEN DE AHORRO"]
        lines.append("-" * 40)
        
        if 'health_score' in savings:
            score = savings['health_score']
            status = "⭐ Excelente" if score > 80 else "🟡 Bueno" if score > 60 else "🔴 Necesita mejora"
            lines.append(f"Salud financiera: {score}% {status}")
        
        if 'tips' in savings:
            lines.append("\nRecomendaciones:")
            for tip in savings['tips']:
                lines.append(f"  • {tip}")
        
        if 'goals' in savings:
            lines.append("\nMetas de ahorro:")
            for goal in savings['goals']:
                lines.append(f"  • {goal.get('nombre')}: ${goal.get('meta'):.2f}")
        
        return "\n".join(lines)
    
    def get_performance_stats(self) -> str:
        """Estadísticas de rendimiento de la consulta"""
        lines = ["⚡ RENDIMIENTO"]
        lines.append("-" * 40)
        lines.append(f"Tiempo de procesamiento: {self.meta.get('processing_time_ms', 0):.0f}ms")
        lines.append(f"Timestamp: {self.meta.get('timestamp', 'N/A')}")
        lines.append(f"Nivel de análisis: {self.meta.get('nivel', 'N/A')}")
        lines.append(f"Cache hit: {self.meta.get('cache_hit', False)}")
        
        return "\n".join(lines)
    
    def print_report(self):
        """Imprimir reporte completo"""
        print(self.get_prediction_summary())
        print("\n")
        print(self.get_savings_summary())
        print("\n")
        print(self.get_performance_stats())


# ============================================================
# EJEMPLOS DE USO
# ============================================================

if __name__ == "__main__":
    # Configuración
    API_URL = "http://localhost:5000"
    TOKEN = "your_jwt_token_here"
    
    # Crear cliente
    ai = FinancialAI(api_url=API_URL, token=TOKEN)
    
    print("=" * 60)
    print("🚀 FINANCIAL AI - SDK PYTHON")
    print("=" * 60)
    
    try:
        # Ejemplo 1: Análisis rápido
        print("\n1️⃣ ANÁLISIS RÁPIDO (< 2 segundos)")
        print("-" * 60)
        quick = ai.quick_analysis()
        analyzer = FinancialAIAnalyzer(quick)
        analyzer.print_report()
        
        # Ejemplo 2: Análisis completo
        print("\n2️⃣ ANÁLISIS COMPLETO (2-5 segundos)")
        print("-" * 60)
        full = ai.full_analysis()
        analyzer = FinancialAIAnalyzer(full)
        analyzer.print_report()
        
        # Ejemplo 3: Análisis asíncrono
        print("\n3️⃣ ANÁLISIS ASÍNCRONO (PROFUNDO)")
        print("-" * 60)
        
        # Iniciar análisis sin esperar
        result = ai.queue_analysis(wait=False)
        job_id = result['data']['job_id']
        print(f"Job encolado: {job_id}")
        print(f"Tiempo estimado: {result['data']['estimated_time_seconds']}s")
        
        # Verificar estado
        print("\nVerificando estado...")
        status = ai.check_job(job_id)
        print(f"Estado: {status['data']['status']}")
        
        # Esperar a que termine
        print("\nEsperando a que se complete...")
        completed = ai.queue_analysis(job_id=job_id, wait=True)
        print(f"✅ Análisis completado!")
        
    except FinancialAIError as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 60)
