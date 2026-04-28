import { cn } from '@/lib/cn';
import { useUIStore } from '../stores/ui-store';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './Dialog';

export function DialogManager() {
  const dialog = useUIStore((s) => s.dialog);
  const closeDialog = useUIStore((s) => s.closeDialog);

  return (
    <Dialog open={dialog.isOpen} onOpenChange={(open) => !open && closeDialog()}>
      <DialogContent className={cn('space-y-4', dialog.contentClass)}>
        {dialog.title && (
          <DialogHeader className="px-2">
            <DialogTitle className={cn('text-white font-semibold text-xl', dialog.titleClass)}>
              {dialog.title}
            </DialogTitle>
            <DialogDescription className={cn('text-white/60', dialog.descriptionClass)}>
              {dialog.description}
            </DialogDescription>
          </DialogHeader>
        )}
        <div className="px-2">{dialog.isOpen && dialog.content}</div>
      </DialogContent>
    </Dialog>
  );
}
