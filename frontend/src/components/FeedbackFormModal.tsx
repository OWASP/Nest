import { Button } from '@chakra-ui/react'
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogRoot,
  DialogTrigger,
} from 'components/ui/Dialog'
import { FeedbackForm } from './FeedbackForm'

export const FeedbackFormModal = () => {
  return (
    <DialogRoot motionPreset="slide-in-bottom" placement="center">
      <DialogTrigger asChild>
        <Button size="sm">Feedback</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogBody>
          <FeedbackForm />
        </DialogBody>
        <DialogCloseTrigger top="0" insetEnd="-12" bg="bg" />
      </DialogContent>
    </DialogRoot>
  )
}
