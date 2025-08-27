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
      className={[
        'w-screen', 
        className,
      ].join(' ')}
      
      // Framer Motion props:
      whileHover={{ scale: 1.03, boxShadow: '0 10px 15px rgba(0,0,0,0.1)' }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      style={{ width: '100%' }}
    >
      <h3 className={`text-lg font-semibold mb-2 ${titleClassName}`}>
        {title}
      </h3>
      {children}
    </motion.article>
  );
}


