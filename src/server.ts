import express, { Request, Response } from 'express';
import * as cron from 'node-cron';
import * as dotenv from 'dotenv';
import { EmailProcessor } from './emailProcessor';
import { Parser, ParsedData } from './parser';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;
const CRON_SCHEDULE = process.env.CRON_SCHEDULE || '*/2 * * * *';

const emailProcessor = new EmailProcessor();
const parser = new Parser();

let cachedData: ParsedData | null = null;
let lastProcessedTime: Date | null = null;

async function fetchAndParseLatestAttachment(): Promise<void> {
  try {
    console.log('\n' + '='.repeat(80));
    console.log('Starting email fetch and parse process...');
    console.log('Time:', new Date().toLocaleString());
    console.log('='.repeat(80) + '\n');

    const attachment = await emailProcessor.fetchLatestAttachment();

    if (!attachment) {
      console.log('No new attachments found to process');
      return;
    }

    console.log(`\nSuccessfully fetched attachment: ${attachment.filename}`);

    const parsedData = await parser.parseAttachment(attachment.filename, attachment.content);
    const tableOutput = parser.formatAsTable(parsedData, 20);
    console.log(tableOutput);

    const summary = parser.getSummary(parsedData);
    console.log(summary);

    cachedData = parsedData;
    lastProcessedTime = new Date();

    console.log('\nProcessing completed successfully!\n');

  } catch (error) {
    console.error('\nError during processing:', error);
    
    if (error instanceof Error) {
      console.error('Error details:', error.message);
    }
  }
}

app.use(express.json());

app.get('/', (req: Request, res: Response) => {
  res.json({
    status: 'running',
    message: 'Email Attachment Parser',
    uptime: process.uptime(),
    lastProcessed: lastProcessedTime,
    cronSchedule: CRON_SCHEDULE
  });
});

app.get('/api/latest', (req: Request, res: Response) => {
  if (!cachedData) {
    return res.status(404).json({
      error: 'No data available yet. Waiting for first cron run...'
    });
  }

  res.json({
    data: cachedData,
    processedAt: lastProcessedTime,
    summary: {
      filename: cachedData.filename,
      rows: cachedData.rowCount,
      columns: cachedData.columnCount,
      columnNames: cachedData.columns
    }
  });
});

app.get('/api/table', (req: Request, res: Response) => {
  if (!cachedData) {
    return res.status(404).json({
      error: 'No data available yet. Waiting for first cron run...'
    });
  }

  const tableOutput = parser.formatAsTable(cachedData, 50);
  
  res.type('text/plain').send(tableOutput);
});

app.post('/api/trigger', async (req: Request, res: Response) => {
  res.json({
    message: 'Manual trigger initiated',
    timestamp: new Date()
  });

  fetchAndParseLatestAttachment();
});

app.get('/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date(),
    uptime: process.uptime()
  });
});

async function startServer(): Promise<void> {
  try {
    app.listen(PORT, () => {
      console.log('\n' + '='.repeat(80));
      console.log('EMAIL ATTACHMENT PARSER');
      console.log('='.repeat(80));
      console.log(`\nServer running on http://localhost:${PORT}`);
      console.log('\nAvailable endpoints:');
      console.log(`   GET  /              - Server status`);
      console.log(`   GET  /api/latest    - Latest parsed data (JSON)`);
      console.log(`   GET  /api/table     - Latest data as table (text)`);
      console.log(`   POST /api/trigger   - Manually trigger parsing`);
      console.log(`   GET  /health        - Health check`);
      console.log(`\nCron Schedule: ${CRON_SCHEDULE}`);
      console.log('='.repeat(80) + '\n');
    });

    cron.schedule(CRON_SCHEDULE, () => {
      console.log('\nCron job triggered');
      fetchAndParseLatestAttachment();
    });

    console.log(`Cron job scheduled: ${CRON_SCHEDULE}\n`);
    console.log('Running initial fetch...\n');
    await fetchAndParseLatestAttachment();

  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

process.on('SIGINT', () => {
  console.log('\n\nShutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n\nShutting down gracefully...');
  process.exit(0);
});

// Start the application
startServer();
