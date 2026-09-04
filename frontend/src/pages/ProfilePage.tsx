import ProfilePanel from '../components/profile/ProfilePanel';

interface ProfilePageProps {
  userId: string;
}

export default function ProfilePage({ userId }: ProfilePageProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-6 shadow-futuristic">
        <h2 className="text-2xl font-semibold text-white">User Profile & Intelligence</h2>
        <p className="mt-1 text-xs text-slate-400">
          Persistent user profile summary derived from conversation history and memory extraction.
        </p>
      </div>

      <ProfilePanel userId={userId} />
    </div>
  );
}
