import Link from 'next/link';
import { Boss } from './data';

export default function BossCard({ boss }: { boss: Boss }) {
  const difficultyColors: Record<string, string> = {
    Easy: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    Medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    Hard: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
    Extreme: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  };

  return (
    <Link
      href={`/bosses/${boss.slug}`}
      className="block p-4 rounded-lg border border-gray-200 dark:border-gray-800 hover:border-blue-400 dark:hover:border-blue-600 transition-colors group"
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold group-hover:text-blue-600 transition-colors">{boss.name}</h3>
        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${difficultyColors[boss.difficulty] || 'bg-gray-100'}`}>
          {boss.difficulty}
        </span>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-3">
        {boss.description}
      </p>
      <div className="flex flex-wrap gap-1">
        {boss.tags.slice(0, 3).map((tag) => (
          <span key={tag} className="text-xs px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400">
            {tag}
          </span>
        ))}
      </div>
    </Link>
  );
}
