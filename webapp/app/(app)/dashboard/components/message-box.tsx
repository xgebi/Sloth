import styles from "@/app/(app)/dashboard/dashboard.module.css";
import commonBoxStyles from './common-box.module.css';
import msgBoxStyles from './message-box.module.css';

interface MessageBoxProps {
	messages: [{
		uuid: string,
		sentDate: string,
		status: string
	}]
}

export default function MessageBox({ messages }: MessageBoxProps) {
	return <section className={commonBoxStyles.card}>
			<h2>Messages</h2>
			<hr />
			{messages.length <= 0 && <div className={commonBoxStyles['no-posts-message']}>No posts</div>}
			{messages.map((msg) => {
				const classes = `${msgBoxStyles['message']} ${msg.status === 'unread' ? msgBoxStyles['unread'] :  ''}`.trim()
				return (
					<article key={msg.uuid}>
						<h3><a href={`/dashboard/messages/${msg.uuid}`} className={classes}>Message from {msg.sentDate}</a></h3>
					</article>
				)
			})}
		</section>
}