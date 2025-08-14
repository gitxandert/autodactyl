import { motion } from 'framer-motion';

type Props = {
  title: string;
  children: React.ReactNode;
  className?: string;
  titleClassName?: string;
};

export default function Card({
  title,
  children,
  className = "",
  titleClassName = "",
}: Props) {
  return (
    <motion.article
      // your base styling
      className={[
        'rounded-xl',
        'shadow-md',
        'p-6',
        'mb-5',
        className,
      ].join(' ')}
      
      // Framer Motion props:
      whileHover={{ scale: 1.03, boxShadow: '0 10px 15px rgba(0,0,0,0.1)' }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      <h3 className={`text-lg font-semibold mb-2 ${titleClassName}`}>
        {title}
      </h3>
      {children}
    </motion.article>
  );
}


