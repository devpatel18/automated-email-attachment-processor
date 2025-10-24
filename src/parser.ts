import csv from 'csv-parser';
import * as XLSX from 'xlsx';
import { Readable } from 'stream';
import Table from 'cli-table3';

export interface ParsedData {
  filename: string;
  rows: any[];
  columns: string[];
  rowCount: number;
  columnCount: number;
}

export class Parser {
  public async parseAttachment(filename: string, content: Buffer): Promise<ParsedData> {
    const ext = filename.toLowerCase().split('.').pop();

    console.log(`\nParsing ${ext?.toUpperCase()} file: ${filename}`);
    console.log(`File size: ${(content.length / 1024).toFixed(2)} KB`);

    let parsedData: ParsedData;

    if (ext === 'csv') {
      parsedData = await this.parseCSV(filename, content);
    } else if (ext === 'xlsx' || ext === 'xls') {
      parsedData = await this.parseExcel(filename, content);
    } else {
      throw new Error(`Unsupported file type: ${ext}`);
    }

    console.log(`Parsed ${parsedData.rowCount} rows and ${parsedData.columnCount} columns`);
    return parsedData;
  }

  private async parseCSV(filename: string, content: Buffer): Promise<ParsedData> {
    return new Promise((resolve, reject) => {
      const rows: any[] = [];
      let columns: string[] = [];

      const stream = Readable.from(content);

      stream
        .pipe(csv())
        .on('headers', (headers: string[]) => {
          columns = headers;
        })
        .on('data', (row: any) => {
          rows.push(row);
        })
        .on('end', () => {
          resolve({
            filename,
            rows,
            columns,
            rowCount: rows.length,
            columnCount: columns.length
          });
        })
        .on('error', (err: Error) => {
          reject(err);
        });
    });
  }

  private async parseExcel(filename: string, content: Buffer): Promise<ParsedData> {
    try {
      const workbook = XLSX.read(content, { type: 'buffer' });

      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];

      console.log(`Reading sheet: ${sheetName}`);

      const jsonData: any[] = XLSX.utils.sheet_to_json(worksheet);
      
      const columns = jsonData.length > 0 ? Object.keys(jsonData[0]) : [];

      return {
        filename,
        rows: jsonData,
        columns,
        rowCount: jsonData.length,
        columnCount: columns.length
      };
    } catch (error) {
      throw new Error(`Failed to parse Excel file: ${error}`);
    }
  }

  public formatAsTable(data: ParsedData, maxRows: number = 10): string {
    if (data.rows.length === 0) {
      return 'No data to display';
    }

    const table = new Table({
      head: data.columns,
      style: {
        head: ['cyan', 'bold'],
        border: ['gray']
      },
      colWidths: data.columns.map(() => 20),
      wordWrap: true
    });

    const displayRows = data.rows.slice(0, maxRows);
    
    displayRows.forEach(row => {
      const values = data.columns.map(col => {
        const value = row[col];
        if (value && String(value).length > 50) {
          return String(value).substring(0, 47) + '...';
        }
        return value || '';
      });
      table.push(values);
    });

    let output = '\n' + '='.repeat(80) + '\n';
    output += `Data from: ${data.filename}\n`;
    output += `Total Rows: ${data.rowCount} | Columns: ${data.columnCount}\n`;
    
    if (data.rowCount > maxRows) {
      output += `Showing first ${maxRows} of ${data.rowCount} rows\n`;
    }
    
    output += '='.repeat(80) + '\n\n';
    output += table.toString();
    output += '\n' + '='.repeat(80) + '\n';

    return output;
  }

  public getSummary(data: ParsedData): string {
    let summary = '\nDATA SUMMARY\n';
    summary += '─'.repeat(40) + '\n';
    summary += `Filename: ${data.filename}\n`;
    summary += `Rows: ${data.rowCount}\n`;
    summary += `Columns: ${data.columnCount}\n`;
    summary += `Column Names: ${data.columns.join(', ')}\n`;
    summary += '─'.repeat(40) + '\n';

    return summary;
  }
}
