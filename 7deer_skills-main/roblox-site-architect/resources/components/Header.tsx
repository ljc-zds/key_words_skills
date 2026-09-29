import Link from 'next/link';
import { getGameConfig } from '@/lib/data';

const config = getGameConfig();

export default function Header() {
  return (
    <header className="border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/" className="font-bold text-lg tracking-tight hover:text-blue-600 transition-colors">
          🏰 {config.game.name}
          <span className="text-xs text-gray-400 ml-2 font-normal hidden sm:inline">Guide & Tools</span>
        </Link>
        <nav className="flex items-center gap-1 text-sm font-medium">
          <Link href="/bosses" className="px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            Bosses
          </Link>
          <Link href="/tier-list" className="px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            Tier List
          </Link>
          <Link href="/codes" className="px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            Codes
          </Link>
          <Link href="/simulator" className="px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            Simulator
          </Link>
          <Link href="/updates" className="px-3 py-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            Updates
          </Link>
        </nav>
      </div>
    </header>
  );
}
