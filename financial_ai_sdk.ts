/**
 * FinancialAI SDK - Cliente TypeScript/JavaScript
 * 
 * Uso:
 *   const ai = new FinancialAI({ apiUrl: 'http://localhost:5000', token: 'YOUR_TOKEN' });
 *   const result = await ai.fullAnalysis();
 */

export interface AnalysisOptions {
  includeCharts?: boolean;
  cacheTTL?: number;
  timeout?: number;
}

export interface PredictionData {
  categoria?: Record<string, number>;
  mensual?: Record<string, number>;
  anomalias?: {
    detectadas: number;
    porcentaje: number;
  };
  modelos?: Record<string, number>;
  [key: string]: any;
}

export interface StatisticsData {
  correlaciones?: Record<string, number>;
  tendencias?: {
    promedio_diario: number;
    máximo: number;
    mínimo: number;
  };
  clustering?: {
    grupos: number;
    varianza: number;
  };
  [key: string]: any;
}

export interface SavingsData {
  goals?: Array<{
    nombre: string;
    meta: number;
    prioridad: string;
  }>;
  tips?: string[];
  budget_alerts?: {
    limite_recomendado: number;
    limite_maximo: number;
  };
  health_score?: number;
  [key: string]: any;
}

export interface ChartsData {
  heatmap?: Record<string, any>;
  sankey?: Record<string, any>;
  dashboard?: {
    total_gastos: number;
    gastos_promedio: number;
    categorias: number;
  };
  [key: string]: any;
}

export interface AnalysisResult {
  success: boolean;
  data: {
    usuario_id: string;
    prediccion?: PredictionData;
    estadisticas?: StatisticsData;
    ahorro?: SavingsData;
    graficos?: ChartsData;
  };
  meta: {
    processing_time_ms: number;
    timestamp: string;
    cache_hit: boolean;
    nivel: 'quick' | 'full';
    modelos_utilizados?: string[];
  };
  errors?: string[];
}

export interface JobResult {
  success: boolean;
  data: {
    job_id: string;
    usuario_id: string;
    status: 'queued' | 'processing' | 'completed' | 'error';
    resultado?: any;
    error?: string;
    timestamp?: string;
  };
}

export class FinancialAIError extends Error {
  constructor(message: string, public statusCode?: number) {
    super(message);
    this.name = 'FinancialAIError';
  }
}

export class FinancialAI {
  private apiUrl: string;
  private token: string;
  private timeout: number;
  private cache: Map<string, { data: any; timestamp: number }>;
  private cacheTTL: number;

  constructor(options: {
    apiUrl: string;
    token: string;
    timeout?: number;
    cacheTTL?: number;
  }) {
    this.apiUrl = options.apiUrl.replace(/\/$/, '');
    this.token = options.token;
    this.timeout = options.timeout || 30000;
    this.cacheTTL = options.cacheTTL || 300000; // 5 minutos por defecto
    this.cache = new Map();
  }

  /**
   * Realizar request a la API
   */
  private async request<T>(
    method: string,
    endpoint: string,
    body?: any
  ): Promise<T> {
    const url = `${this.apiUrl}${endpoint}`;
    const cacheKey = `${method}:${endpoint}`;

    // Verificar caché
    if (method === 'GET') {
      const cached = this.cache.get(cacheKey);
      if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
        return cached.data;
      }
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new FinancialAIError(
          `API Error: ${response.statusText}`,
          response.status
        );
      }

      const data = await response.json();

      if (!data.success) {
        throw new FinancialAIError(data.error || 'Unknown error');
      }

      // Guardar en caché
      if (method === 'GET') {
        this.cache.set(cacheKey, { data, timestamp: Date.now() });
      }

      return data;
    } catch (error) {
      if (error instanceof FinancialAIError) {
        throw error;
      }
      if (error instanceof TypeError) {
        throw new FinancialAIError('Network error or API unreachable');
      }
      throw new FinancialAIError(
        error instanceof Error ? error.message : 'Unknown error'
      );
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Análisis rápido (< 2 segundos)
   */
  async quickAnalysis(): Promise<AnalysisResult> {
    return this.request<AnalysisResult>(
      'POST',
      '/api/v2/analysis/quick'
    );
  }

  /**
   * Análisis completo (2-5 segundos)
   */
  async fullAnalysis(): Promise<AnalysisResult> {
    return this.request<AnalysisResult>(
      'POST',
      '/api/v2/analysis/full'
    );
  }

  /**
   * Encolar análisis profundo (asíncrono)
   */
  async queueAnalysis(): Promise<JobResult> {
    return this.request<JobResult>(
      'POST',
      '/api/v2/analysis/queue'
    );
  }

  /**
   * Verificar estado de un job
   */
  async checkJob(jobId: string): Promise<JobResult> {
    return this.request<JobResult>(
      'GET',
      `/api/v2/analysis/job/${jobId}`
    );
  }

  /**
   * Esperar a que un job se complete
   */
  async waitForJob(
    jobId: string,
    options: { timeout?: number; pollInterval?: number } = {}
  ): Promise<any> {
    const timeout = options.timeout || 120000; // 2 minutos
    const pollInterval = options.pollInterval || 2000; // 2 segundos
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const result = await this.checkJob(jobId);
      const status = result.data.status;

      if (status === 'completed') {
        return result.data.resultado;
      }

      if (status === 'error') {
        throw new FinancialAIError(
          result.data.error || 'Job failed'
        );
      }

      await new Promise((resolve) => setTimeout(resolve, pollInterval));
    }

    throw new FinancialAIError(`Timeout waiting for job ${jobId}`);
  }

  /**
   * Ejecutar análisis completo con espera
   */
  async fullAnalysisAsync(
    options: { timeout?: number; pollInterval?: number } = {}
  ): Promise<any> {
    const queueResult = await this.queueAnalysis();
    const jobId = queueResult.data.job_id;
    return this.waitForJob(jobId, options);
  }

  /**
   * Cancelar caché
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Obtener estadísticas del caché
   */
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
    };
  }
}

/**
 * Hook React para usar FinancialAI
 */
export function useFinancialAI(token: string, apiUrl: string = 'http://localhost:5000') {
  const [ai] = React.useState(() => new FinancialAI({ apiUrl, token }));

  const [state, setState] = React.useState<{
    data: AnalysisResult | null;
    loading: boolean;
    error: FinancialAIError | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const quickAnalysis = React.useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const result = await ai.quickAnalysis();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const err = error instanceof FinancialAIError ? error : new FinancialAIError(String(error));
      setState({ data: null, loading: false, error: err });
      throw err;
    }
  }, [ai]);

  const fullAnalysis = React.useCallback(async () => {
    setState({ data: null, loading: true, error: null });
    try {
      const result = await ai.fullAnalysis();
      setState({ data: result, loading: false, error: null });
      return result;
    } catch (error) {
      const err = error instanceof FinancialAIError ? error : new FinancialAIError(String(error));
      setState({ data: null, loading: false, error: err });
      throw err;
    }
  }, [ai]);

  return { ...state, quickAnalysis, fullAnalysis };
}

/**
 * Formatter para mostrar resultados
 */
export class AnalysisFormatter {
  static formatPredictionSummary(pred: PredictionData): string {
    const lines: string[] = [];
    lines.push('📊 PREDICCIONES');

    if (pred.categoria) {
      lines.push('\nGastos por categoría:');
      Object.entries(pred.categoria).forEach(([cat, amount]) => {
        lines.push(`  • ${cat}: $${(amount as number).toFixed(2)}`);
      });
    }

    if (pred.anomalias) {
      lines.push(`\nAnomalías: ${pred.anomalias.detectadas} (${pred.anomalias.porcentaje.toFixed(1)}%)`);
    }

    return lines.join('\n');
  }

  static formatSavingsSummary(savings: SavingsData): string {
    const lines: string[] = [];
    lines.push('💰 AHORRO');

    if (savings.health_score) {
      const score = savings.health_score;
      const status = score > 80 ? '⭐ Excelente' : score > 60 ? '🟡 Bueno' : '🔴 Necesita mejora';
      lines.push(`\nSalud financiera: ${score}% ${status}`);
    }

    if (savings.tips && savings.tips.length > 0) {
      lines.push('\nRecomendaciones:');
      savings.tips.forEach((tip) => {
        lines.push(`  • ${tip}`);
      });
    }

    return lines.join('\n');
  }

  static formatReport(result: AnalysisResult): string {
    const lines: string[] = [];

    if (result.data.prediccion) {
      lines.push(this.formatPredictionSummary(result.data.prediccion));
    }

    if (result.data.ahorro) {
      lines.push('\n' + this.formatSavingsSummary(result.data.ahorro));
    }

    lines.push(`\n⚡ Procesamiento: ${result.meta.processing_time_ms}ms`);

    return lines.join('\n');
  }
}

// ============================================================
// EJEMPLOS DE USO
// ============================================================

if (typeof window !== 'undefined') {
  // Ejemplo React
  const Example: React.FC = () => {
    const token = localStorage.getItem('token') || '';
    const { data, loading, error, fullAnalysis } = useFinancialAI(token);

    React.useEffect(() => {
      fullAnalysis();
    }, [fullAnalysis]);

    if (loading) return <div>Analizando...</div>;
    if (error) return <div>Error: {error.message}</div>;
    if (!data) return null;

    return (
      <div>
        <h1>Análisis Financiero</h1>
        <pre>{AnalysisFormatter.formatReport(data)}</pre>
        <p>Tiempo: {data.meta.processing_time_ms}ms</p>
      </div>
    );
  };

  // Ejemplo vanilla JavaScript
  async function exampleVanilla() {
    const ai = new FinancialAI({
      apiUrl: 'http://localhost:5000',
      token: 'your_token_here',
    });

    try {
      const result = await ai.fullAnalysis();
      console.log(AnalysisFormatter.formatReport(result));
    } catch (error) {
      console.error('Error:', error);
    }
  }
}

export default FinancialAI;
