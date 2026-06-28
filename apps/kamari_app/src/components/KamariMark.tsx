interface Props {
  size?: number;
  /** 'gold' for dark backgrounds, 'indigo' for light ones */
  tone?: 'gold' | 'indigo';
}

/** Adinkra-inspired Kámárí glyph — a diamond with radiating marks and a clay centre. */
export default function KamariMark({ size = 64, tone = 'gold' }: Props) {
  const stroke = tone === 'gold' ? '#E8B84B' : '#213A6B';
  return (
    <svg width={size} height={size} viewBox="0 0 512 512" aria-label="Kámárí" role="img">
      <g fill="none" stroke={stroke} strokeWidth={14} strokeLinejoin="round" strokeLinecap="round">
        <path d="M256 96 416 256 256 416 96 256 Z" />
        <path d="M256 168 344 256 256 344 168 256 Z" />
        <path d="M256 56v36M256 420v36M56 256h36M420 256h36" />
      </g>
      <circle cx="256" cy="256" r="26" fill="#C65D3B" />
    </svg>
  );
}
