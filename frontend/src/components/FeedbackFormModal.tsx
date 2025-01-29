import { Button } from '@chakra-ui/react'
import { faQuestionCircle } from '@fortawesome/free-regular-svg-icons'
import { faCircleQuestion } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogRoot,
  DialogTrigger,
} from 'components/ui/Dialog'
import { Tooltip } from "components/ui/tooltip"
import { FeedbackForm } from './FeedbackForm'

export const FeedbackFormModal = () => {
  return (
    <DialogRoot motionPreset="slide-in-bottom" placement="center">
      <Tooltip
        showArrow
        content="Give Feedback"
        openDelay={500}
        closeDelay={100}
      >
        <DialogTrigger asChild>

          <Button size="sm" variant={'outline'} colorScheme="blue" className="group flex items-center border">
            <FontAwesomeIcon icon={faCircleQuestion} className="group-hover:block hidden transition-all ease-linear" />
            <FontAwesomeIcon icon={faQuestionCircle} className="group-hover:hidden block transition-all ease-linear" />
          </Button>
        </DialogTrigger>
      </Tooltip>
      <DialogContent>
        <DialogBody>
          <FeedbackForm />
        </DialogBody>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}
