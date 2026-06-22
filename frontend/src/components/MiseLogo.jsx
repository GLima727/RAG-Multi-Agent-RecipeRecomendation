const sizes = {
  sm: { box: 28, text: 'text-lg' },
  md: { box: 36, text: 'text-2xl' },
  lg: { box: 48, text: 'text-4xl' },
}

export function MiseLogo({ size = 'md' }) {
  const { box, text } = sizes[size]

  return (
    <div className="flex items-center gap-2.5 select-none">
      <svg width={box} height={box} viewBox="0 0 36 36" fill="none" aria-hidden="true">
        <rect width="36" height="36" rx="8" fill="#e8a838" />
        {/* M glyph */}
        <path
          d="M8 27V10l10 10 10-10v17"
          stroke="#1a1a1a"
          strokeWidth="2.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span className={`${text} font-serif text-cream tracking-wide leading-none`}>
        mise
      </span>
    </div>
  )
}
