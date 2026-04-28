import { Skeleton } from '@/features/shared/ui/Skeleton';

export function LoginSkeleton() {
  return (
    <div className="min-h-screen flex items-center justify-center pt-20">
      <div className="w-full max-w-md px-4">
        <Skeleton className="h-10 w-64 mx-auto mb-8" />
        <Skeleton className="h-64 w-full mb-8" />

        <div className="space-y-4">
          <div>
            <Skeleton className="h-5 w-16 mb-2" />
            <Skeleton className="h-11 w-full" />
          </div>

          <div>
            <Skeleton className="h-5 w-20 mb-2" />
            <Skeleton className="h-11 w-full" />
          </div>

          <Skeleton className="h-12 w-full" />

          <Skeleton className="h-5 w-64 mx-auto" />
        </div>

        <Skeleton className="h-6 w-80 mx-auto mt-8" />
      </div>
    </div>
  );
}
