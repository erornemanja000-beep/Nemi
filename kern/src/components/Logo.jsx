// KERN znak: slovo K čiji se krakovi sastaju u užarenom jezgru („Kern“)
export function Mark({ className = 'mark', title }) {
  return (
    <svg className={className} viewBox="0 0 48 48" role={title ? 'img' : undefined} aria-hidden={title ? undefined : true} aria-label={title}>
      <path fill="currentColor" d="M11 9h6v30h-6z" />
      <path fill="currentColor" d="M22.6 21.2 34.2 9h7.6L27.2 24.4zM22.6 26.8l4.6-2.4L41.8 39h-7.6z" />
      <circle cx="24" cy="24" r="4.6" fill="var(--accent)" />
    </svg>
  );
}

export function Logo({ className = '' }) {
  return (
    <span className={`logo ${className}`}>
      <Mark />
      <span className="logo-word">KERN</span>
    </span>
  );
}
