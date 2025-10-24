import Imap from 'imap';
import { simpleParser, ParsedMail } from 'mailparser';
import * as dotenv from 'dotenv';

dotenv.config();

interface EmailAttachment {
  filename: string;
  content: Buffer;
  contentType: string;
  size: number;
}

interface EmailConfig {
  user: string;
  password: string;
  host: string;
  port: number;
  tls: boolean;
  tlsOptions: {
    rejectUnauthorized: boolean;
  };
}

export class EmailProcessor {
  private config: EmailConfig;
  private targetSenders: string[];
  private targetSubject: string;

  constructor() {
    this.config = {
      user: process.env.EMAIL_ADDRESS || '',
      password: process.env.EMAIL_PASSWORD || '',
      host: process.env.IMAP_SERVER || 'imap.gmail.com',
      port: parseInt(process.env.IMAP_PORT || '993'),
      tls: true,
      tlsOptions: {
        rejectUnauthorized: false
      }
    };

    const sendersEnv = process.env.TARGET_SENDERS || '';
    this.targetSenders = sendersEnv
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0);
    
    this.targetSubject = process.env.TARGET_SUBJECT || '';

    this.validateConfig();
  }

  private validateConfig(): void {
    if (!this.config.user || !this.config.password) {
      throw new Error('Email credentials not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD in .env');
    }

    if (this.targetSenders.length === 0) {
      console.warn('Warning: TARGET_SENDERS not set. Will process emails from all senders.');
    } else {
      console.log(`Filtering emails from ${this.targetSenders.length} sender(s): ${this.targetSenders.join(', ')}`);
    }

    if (this.targetSubject) {
      console.log(`Filtering by subject: "${this.targetSubject}"`);
    }
  }

  public async fetchLatestAttachment(): Promise<EmailAttachment | null> {
    return new Promise((resolve, reject) => {
      console.log('Connecting to email server...');
      
      const imap = new Imap(this.config);
      let latestAttachment: EmailAttachment | null = null;

      imap.once('ready', () => {
        console.log('Connected to email server');
        
        imap.openBox('INBOX', false, (err, box) => {
          if (err) {
            imap.end();
            return reject(err);
          }

          console.log(`Inbox opened. Total messages: ${box.messages.total}`);

          let searchCriteria: any[];
          
          if (this.targetSenders.length > 0) {
            if (this.targetSenders.length === 1) {
              searchCriteria = [['FROM', this.targetSenders[0]]];
            } else {
              searchCriteria = [['OR', ...this.targetSenders.map(sender => ['FROM', sender])]];
            }
          } else {
            searchCriteria = ['ALL'];
          }

          imap.search(searchCriteria, (err: any, results: any) => {
            if (err) {
              imap.end();
              return reject(err);
            }

            if (!results || results.length === 0) {
              const senderInfo = this.targetSenders.length > 0 
                ? this.targetSenders.join(', ') 
                : 'any sender';
              console.log(`No emails found from ${senderInfo}`);
              imap.end();
              return resolve(null);
            }

            const senderInfo = this.targetSenders.length > 0 
              ? this.targetSenders.join(', ') 
              : 'all senders';
            console.log(`Found ${results.length} email(s) from ${senderInfo}`);

            const latestEmailUid = results[results.length - 1];
            
            const fetch = imap.fetch([latestEmailUid], {
              bodies: '',
              struct: true
            });

            fetch.on('message', (msg, seqno) => {
              console.log(`Processing message #${seqno}`);

              msg.on('body', (stream, info) => {
                simpleParser(stream, async (err: any, parsed: ParsedMail) => {
                  if (err) {
                    console.error('Error parsing email:', err);
                    return;
                  }

                  console.log(`Email Subject: ${parsed.subject}`);
                  console.log(`From: ${parsed.from?.text}`);
                  console.log(`Date: ${parsed.date}`);

                  if (this.targetSenders.length > 0) {
                    const fromAddress = parsed.from?.value[0]?.address?.toLowerCase() || '';
                    const isFromTargetSender = this.targetSenders.some(
                      sender => fromAddress.includes(sender.toLowerCase())
                    );
                    
                    if (!isFromTargetSender) {
                      console.log('Skipping - sender not in target list');
                      return;
                    }
                  }

                  if (this.targetSubject && parsed.subject) {
                    const subjectMatch = parsed.subject.toLowerCase().includes(this.targetSubject.toLowerCase());
                    if (!subjectMatch) {
                      console.log(`Skipping - subject doesn't match filter: "${this.targetSubject}"`);
                      return;
                    }
                    console.log(`Subject matches filter: "${this.targetSubject}"`);
                  }

                  if (parsed.attachments && parsed.attachments.length > 0) {
                    console.log(`Found ${parsed.attachments.length} attachment(s)`);

                    for (const attachment of parsed.attachments) {
                      const filename = attachment.filename || 'unknown';
                      const ext = filename.toLowerCase().split('.').pop();

                      if (ext === 'csv' || ext === 'xlsx' || ext === 'xls') {
                        console.log(`Found ${ext.toUpperCase()} attachment: ${filename}`);
                        
                        latestAttachment = {
                          filename: filename,
                          content: attachment.content,
                          contentType: attachment.contentType,
                          size: attachment.size
                        };
                        
                        break;
                      }
                    }

                    if (!latestAttachment) {
                      console.log('No CSV/Excel attachments found in this email');
                    }
                  } else {
                    console.log('No attachments found in this email');
                  }
                });
              });

              msg.once('end', () => {
                console.log('Finished processing message');
              });
            });

            fetch.once('error', (err) => {
              console.error('Fetch error:', err);
              imap.end();
              reject(err);
            });

            fetch.once('end', () => {
              console.log('Done fetching messages');
              imap.end();
            });
          });
        });
      });

      imap.once('error', (err: any) => {
        console.error('IMAP error:', err);
        reject(err);
      });

      imap.once('end', () => {
        console.log('Disconnected from email server');
        resolve(latestAttachment);
      });

      imap.connect();
    });
  }
}
