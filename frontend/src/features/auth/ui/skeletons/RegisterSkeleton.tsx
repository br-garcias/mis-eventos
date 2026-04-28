import { Skeleton } from '@/features/shared/ui/Skeleton';

export function RegisterSkeleton() {
  return (
    <div className="min-h-screen flex items-center justify-center pt-20">
      <div className="w-full max-w-md px-4">
        <Skeleton className="h-10 w-64 mx-auto mb-8" />
        <Skeleton className="h-80 w-full mb-8" />

        <div className="space-y-4">
          <div>
            <Skeleton className="h-5 w-20 mb-2" />
            <Skeleton className="h-11 w-full" />
          </div>

          <div>
            <Skeleton className="h-5 w-16 mb-2" />
            <Skeleton className="h-11 w-full" />
          </div>

          <div>
            <Skeleton className="h-5 w-20 mb-2" />
            <Skeleton className="h-11 w-full" />
          </div>

          <div>
            <Skeleton className="h-5 w-24 mb-2" />
            <Skeleton className="h-11 w-full" />
          </div>

          <Skeleton className="h-12 w-full" />

          <Skeleton className="h-5 w-64 mx-auto" />
        </div>
      </div>
    </div>
  );
}
