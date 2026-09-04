import { useState } from 'react';
import { HiOutlinePaperClip, HiOutlineX } from 'react-icons/hi';
import { MultimodalPayloadFile } from '../../hooks/useWebSocket';

interface FileUploadProps {
  onFileSelected: (file: MultimodalPayloadFile | null) => void;
}

export default function FileUpload({ onFileSelected }: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<{
    filename: string;
    mime_type: string;
    size_kb: number;
    input_type: string;
  } | null>(null);

  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUploadError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.split('.').pop()?.toLowerCase();
    let inputType = 'image';
    if (['txt', 'md'].includes(ext || '')) {
      inputType = 'document';
    } else if (!['png', 'jpg', 'jpeg', 'webp'].includes(ext || '')) {
      setUploadError(`Unsupported file format .${ext}. Supported: PNG, JPEG, WEBP, .txt, .md`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File exceeds 10 MB size limit.');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64Str = (reader.result as string).split(',')[1] || '';
      const payloadFile: MultimodalPayloadFile = {
        input_type: inputType,
        filename: file.name,
        mime_type: file.type || (inputType === 'image' ? 'image/png' : 'text/plain'),
        content_base64: base64Str,
      };

      setSelectedFile({
        filename: file.name,
        mime_type: payloadFile.mime_type || '',
        size_kb: Math.round(file.size / 1024),
        input_type: inputType,
      });

      onFileSelected(payloadFile);
    };
    reader.readAsDataURL(file);
  };

  const handleClear = () => {
    setSelectedFile(null);
    setUploadError(null);
    onFileSelected(null);
  };

  return (
    <div className="inline-block">
      {!selectedFile ? (
        <label className="flex items-center gap-2 cursor-pointer rounded-2xl border border-white/10 bg-slate-900/80 px-4 py-2.5 text-xs text-slate-300 transition hover:bg-slate-800 hover:text-white">
          <HiOutlinePaperClip size={16} className="text-brand-400" />
          <span>Attach File</span>
          <input
            type="file"
            accept=".png,.jpg,.jpeg,.webp,.txt,.md"
            onChange={handleFileChange}
            className="hidden"
          />
        </label>
      ) : (
        <div className="flex items-center gap-3 rounded-2xl border border-brand-500/30 bg-brand-950/20 px-4 py-2 text-xs text-brand-200">
          <HiOutlinePaperClip size={16} className="text-brand-400 shrink-0" />
          <span className="truncate max-w-[180px] font-medium">{selectedFile.filename}</span>
          <span className="text-[10px] text-slate-400">({selectedFile.size_kb} KB)</span>
          <button
            onClick={handleClear}
            className="rounded-full p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <HiOutlineX size={14} />
          </button>
        </div>
      )}

      {uploadError && <p className="mt-1 text-[11px] text-rose-400">{uploadError}</p>}
    </div>
  );
}
