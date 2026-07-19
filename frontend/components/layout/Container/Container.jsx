import styles from "./Container.module.css";

/**
 * Global horizontal alignment wrapper.
 * Every section uses this to guarantee identical:
 *   max-width: 1400px | margin-inline: auto | padding-inline: 32px
 *
 * Never add padding-block here. That belongs to Section.
 */
export default function Container({ children, className = "" }) {
  return (
    <div className={`${styles.container} ${className}`.trim()}>
      {children}
    </div>
  );
}
