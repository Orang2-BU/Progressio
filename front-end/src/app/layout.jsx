import App from '../App.jsx';
import '../styles.css';

export const metadata = {
  title: { default: 'Progressio — Turning Progress Into Proof', template: '%s — Progressio' },
  description: 'Progressio — ukur kemampuanmu dan ubah kemajuan menjadi bukti.',
};
export const viewport = { themeColor: '#14161d' };

export default function RootLayout({ children }) {
  return <html lang="id"><body><App>{children}</App></body></html>;
}
