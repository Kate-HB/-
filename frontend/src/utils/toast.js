import { inject } from 'vue';
export function useToast() {
  return inject('toast', {
    success: (msg) => alert(msg),
    error: (msg) => alert(msg)
  });
}
