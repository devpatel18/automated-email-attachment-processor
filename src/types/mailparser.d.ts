declare module 'mailparser' {
  export interface ParsedMail {
    subject?: string;
    from?: {
      text: string;
      value: Array<{ address: string; name: string }>;
    };
    to?: {
      text: string;
      value: Array<{ address: string; name: string }>;
    };
    date?: Date;
    text?: string;
    html?: string | false;
    attachments: Array<{
      filename?: string;
      content: Buffer;
      contentType: string;
      size: number;
      headers: Map<string, string>;
    }>;
  }

  export function simpleParser(
    source: NodeJS.ReadableStream | Buffer | string,
    callback: (err: any, parsed: ParsedMail) => void
  ): void;
}
