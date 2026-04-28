import { createElement, ReactNode } from 'react';
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { Button } from '../ui/Button';

interface UIState {
  dialog: {
    isOpen: boolean;
    title: string;
    description: string;
    content: ReactNode | null;
    contentClass?: string;
    titleClass?: string;
    descriptionClass?: string;
  };
}

interface UIActions {
  openDialog: (
    title: string,
    description: string,
    content?: ReactNode,
    contentClass?: string,
    titleClass?: string,
    descriptionClass?: string,
  ) => void;
  closeDialog: () => void;
  confirmDialog: (
    title: string,
    description: string,
    onConfirm: () => void,
    onCancel?: () => void,
    contentClass?: string,
    titleClass?: string,
    descriptionClass?: string,
  ) => void;
}

type UIStore = UIState & UIActions;

export const useUIStore = create<UIStore>()(
  devtools(
    (set, get) => ({
      dialog: {
        isOpen: false,
        title: '',
        description: '',
        content: null,
      },

      openDialog: (
        title,
        description,
        content = null,
        contentClass,
        titleClass,
        descriptionClass,
      ) =>
        set({
          dialog: {
            isOpen: true,
            title,
            description,
            content,
            contentClass,
            titleClass,
            descriptionClass,
          },
        }),

      closeDialog: () =>
        set({
          dialog: {
            isOpen: false,
            title: '',
            description: '',
            content: null,
            contentClass: undefined,
            titleClass: undefined,
            descriptionClass: undefined,
          },
        }),

      confirmDialog: (
        title,
        description,
        onConfirm,
        onCancel,
        contentClass,
        titleClass,
        descriptionClass,
      ) => {
        const ConfirmContent = () => {
          return createElement(
            'div',
            { className: 'flex justify-end gap-2' },
            createElement(
              Button,
              {
                onClick: () => {
                  if (onCancel) onCancel();
                  get().closeDialog();
                },
                variant: 'outline',
              },
              'Cancelar',
            ),
            createElement(
              Button,
              {
                onClick: () => {
                  onConfirm();
                  get().closeDialog();
                },
                variant: 'default',
              },
              'Confirmar',
            ),
          );
        };

        get().openDialog(
          title,
          description,
          createElement(ConfirmContent, null),
          contentClass,
          titleClass,
          descriptionClass,
        );
      },
    }),
    { name: 'ui-store' },
  ),
);
