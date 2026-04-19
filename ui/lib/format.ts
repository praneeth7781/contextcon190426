export function relativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins} min ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 30) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function formatDaysAgo(days: number): string {
  if (days < 30) return `${days} days ago`;
  const months = Math.floor(days / 30);
  if (months < 12) return `${months}mo ago`;
  const years = Math.floor(months / 12);
  return `${years}y ago`;
}

export function getLabColor(lab: string): string {
  const colors: Record<string, string> = {
    Anthropic: "var(--lab-anthropic)",
    OpenAI: "var(--lab-openai)",
    DeepMind: "var(--lab-deepmind)",
    "Google DeepMind": "var(--lab-deepmind)",
    Meta: "var(--lab-meta)",
    "Meta AI": "var(--lab-meta)",
    Google: "var(--lab-google)",
    "Google Brain": "var(--lab-google)",
    Mistral: "var(--lab-mistral)",
    "Mistral AI": "var(--lab-mistral)",
    xAI: "var(--lab-xai)",
    "Scale AI": "var(--lab-scale)",
  };
  return colors[lab] || "var(--lab-default)";
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);
}

export function hashStringToColor(str: string): string {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = hash % 360;
  return `hsl(${hue}, 40%, 35%)`;
}
